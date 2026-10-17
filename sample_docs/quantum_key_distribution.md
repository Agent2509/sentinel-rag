# Quantum Key Distribution and Cryptography

Quantum Key Distribution (QKD) is a secure communication protocol that utilizes the principles
of quantum mechanics to enable two parties to produce a shared random secret key known only
to them. The fundamental security of QKD relies on the laws of physics rather than computational
complexity.

The most famous protocol is BB84, proposed by Charles Bennett and Gilles Brassard in 1984.
In BB84, information is encoded into the polarization states of single photons across non-orthogonal
bases (such as rectilinear and diagonal). According to the Heisenberg uncertainty principle and
the quantum no-cloning theorem, any attempt by an eavesdropper to measure or intercept the quantum
states inevitably disturbs the quantum system. This disturbance introduces measurable errors in
the transmission, allowing the communicating parties to immediately detect eavesdropping.

Once the quantum transmission is complete, the parties perform error reconciliation and privacy
amplification over a conventional authenticated channel to extract a final secret key. This key can
then be used with one-time pad encryption to guarantee information-theoretic secrecy, making it
completely immune to decryption even by future fault-tolerant quantum computers.
