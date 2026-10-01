package soundnessaudit_test

import (
	"errors"
	"math/rand"
	"testing"

	z "example.com/lamp/crypto/zkmap"
	"github.com/consensys/gnark-crypto/ecc/bn254/fr"
)

// These diagnostic tests PASS when the false statement is accepted. They are
// counterexamples to soundness, not tests certifying the implementation.
// Production SetupComplete is used; the attack does not access the trapdoor.
func TestCounterexampleStatementSubstitution(t *testing.T) {
	for _, n := range []int{2, 4, 8} {
		p, err := z.SetupComplete(n, n*n)
		if err != nil {
			t.Fatal(err)
		}
		r := rand.New(rand.NewSource(20261001))
		a := z.RandomMatrix(r, n, n)
		b := z.RandomMatrix(r, n, n)
		c, err := z.Multiply(a, b)
		if err != nil {
			t.Fatal(err)
		}
		s, err := z.CommitMatrices(p.Base(), a, b, c)
		if err != nil {
			t.Fatal(err)
		}
		proof, _, err := z.ProveComplete(p, s, a, b, c)
		if err != nil {
			t.Fatal(err)
		}
		if err = z.VerifyComplete(p, s, *proof); err != nil {
			t.Fatal(err)
		}

		badC := z.Matrix{Rows: n, Cols: n, Data: append([]fr.Element(nil), c.Data...)}
		one := fr.One()
		badC.Data[0].Add(&badC.Data[0], &one) // C'[0,0] = (AB)[0,0] + 1.
		badS, err := z.CommitMatrices(p.Base(), a, b, badC)
		if err != nil {
			t.Fatal(err)
		}
		if s.VC.Equal(&badS.VC) {
			t.Fatal("C commitment did not change")
		}
		y, badY := z.ChallengeComplete(p, s), z.ChallengeComplete(p, badS)
		if y.Equal(&badY) {
			t.Fatal("unexpected challenge collision")
		}
		if _, _, err = z.ProveComplete(p, badS, a, b, badC); !errors.Is(err, z.ErrInnerProductMismatch) {
			t.Fatalf("honest prover should reject incorrect C, got %v", err)
		}

		// Replay the exact honest proof with the incorrect C commitment.
		if err = z.VerifyComplete(p, badS, *proof); err != nil {
			t.Fatalf("counterexample not reproduced: %v", err)
		}
		statementBytes, err := badS.MarshalBinary()
		if err != nil {
			t.Fatal(err)
		}
		proofBytes, err := proof.MarshalBinary()
		if err != nil {
			t.Fatal(err)
		}
		decodedS, err := z.UnmarshalStatement(statementBytes)
		if err != nil {
			t.Fatal(err)
		}
		decodedProof, err := z.UnmarshalCompleteProof(proofBytes)
		if err != nil {
			t.Fatal(err)
		}
		if err = z.VerifyComplete(p, decodedS, decodedProof); err != nil {
			t.Fatal(err)
		}

		// Even rederiving the challenge from the false statement in the prover
		// does not help: the verifier never links the supplied witness to it.
		unrelatedProof, _, err := z.ProveComplete(p, badS, a, b, c)
		if err != nil {
			t.Fatal(err)
		}
		if err = z.VerifyComplete(p, badS, *unrelatedProof); err != nil {
			t.Fatal(err)
		}
		t.Logf("n=%d: C'=AB+E00, VC and challenge changed; replay and decoded replay ACCEPTED; unrelated true witness ACCEPTED", n)
	}
}

func TestCounterexampleAllInfinityProof(t *testing.T) {
	p, err := z.SetupComplete(4, 16)
	if err != nil {
		t.Fatal(err)
	}
	r := rand.New(rand.NewSource(20261001))
	a, b := z.RandomMatrix(r, 4, 4), z.RandomMatrix(r, 4, 4)
	c, err := z.Multiply(a, b)
	if err != nil {
		t.Fatal(err)
	}
	one := fr.One()
	c.Data[0].Add(&c.Data[0], &one)
	s, err := z.CommitMatrices(p.Base(), a, b, c)
	if err != nil {
		t.Fatal(err)
	}
	proof := z.CompleteProof{} // Group identities, without using any witness.
	if err = z.VerifyComplete(p, s, proof); err != nil {
		t.Fatalf("counterexample not reproduced: %v", err)
	}
	binary, err := proof.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	decoded, err := z.UnmarshalCompleteProof(binary)
	if err != nil {
		t.Fatal(err)
	}
	if err = z.VerifyComplete(p, s, decoded); err != nil {
		t.Fatal(err)
	}
	t.Logf("false matrix-product statement ACCEPTED with all-infinity proof, including decoded %d-byte payload", len(binary))
}
