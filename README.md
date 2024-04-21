## Chord Protocol - A Distributed Hash Table
____________________

CHORD is a simple Peer to Peer protocol which implements a Distributed Hash Table detailed as per the paper - [Stoica, Ion, Robert Morris, David Karger, M. Frans Kaashoek, and Hari Balakrishnan. "Chord: A scalable peer-to-peer lookup service for internet applications." ACM SIGCOMM Computer Communication Review 31, no. 4 (2001): 149-160.](https://pdos.csail.mit.edu/papers/chord:sigcomm01/chord_sigcomm.pdf)

This project has two components, the Peer (`HandleNode.py`) and the Client(`Client.py`).

### The Peer:

The Peer program defines a distributed network of nodes that are self-aware of their position in the CHORD architecture, which forms a ring. Each node in the CHORD architecture is aware of its successor and predecessor. When a node joins the CHORD network, it calculates an ID based on its IP and port number. The new node then joins the ring by communicating with any existing node in the ring to find its successor and determine its position in the ring.

There are two types of peer pointers in the CHORD architecture:
1. Successor and Predecessor pointers.
2. Finger table.


#### Finger table

To improve search efficiency, Chord employs a faster method that avoids linear searches. Each node maintains a finger table with up to m entries, where m is the number of bits in the hash key. The ith entry of node n's finger table contains the successor (n + 2^i-1 mod m) for that position. The first entry in the finger table is the node's immediate successor, eliminating the need for an additional successor field. When a node needs to look up a key k, it queries the closest successor or predecessor of k in its finger table (the largest one on the circle with an ID smaller than k), continuing this process until it finds that the key is stored in its immediate successor.

#### Node join

Chord manages concurrent node joins and voluntary departures or failures by employing a basic stabilization protocol. This protocol ensures that nodes' successor pointers remain up to date, ensuring the correctness of lookups. The successor pointers are used to verify and correct finger table entries, ensuring that lookups remain fast and correct.

During stabilization, if joining nodes affect a region of the Chord ring, a lookup occurring before stabilization completes can result in one of three behaviors:

1. In the common case, all involved finger table entries are reasonably current, leading to the lookup finding the correct successor in O(log N) steps.
2. In another case, successor pointers are correct, but finger table entries are outdated, resulting in correct but potentially slower lookups.
3. The final case occurs when nodes in the affected region have incorrect successor pointers, or keys have not yet migrated to newly joined nodes, potentially causing the lookup to fail.

The stabilization scheme guarantees that nodes can be added to a Chord ring in a way that preserves the reachability of existing nodes, even in the presence of concurrent joins and lost or reordered messages.

#### Routing

The routing protocol for operations such as insert, delete, and search in Chord can be summarized as follows:

1. **Hashing**: Hash the object to obtain a key k within the range 0 to 2^m, where m is the number of bits in the hash key.

2. **Routing**: If k is not between the predecessor(n) and n:
    - At node n, send a query for key k to the largest successor/finger entry that is less than or equal to k.
    - If no such entry exists, send a query to successor(n).

3. **Processing**: If k is within the range of predecessor(n) and n, process the query at node n.

The number of hops required for this routing protocol is O(log(N)), where N is the number of peers in the network.

#### Stabilization

To support concurrent joins, a stabilization module has been implemented in the Chord system. This module ensures that all successor pointers are up to date, which is crucial for correct lookups. As a result, a stabilization protocol runs periodically in the background to update finger tables and successor pointers.

The stabilization protocol operates as follows:

1. **Stabilize()**: Node n asks its successor for its predecessor p and determines whether p should be n's successor instead (this is the case if p recently joined the system).

2. **Notify()**: Node n notifies its successor of its existence, allowing the successor to update its predecessor to n.

3. **Fix_fingers()**: This function periodically updates finger tables based on predefined rules to maintain their accuracy and reflect any changes in the network topology.

### Distributed Hash Table Client:

The client program connects to the CHORD network to manage key-value pairs by storing, retrieving, and deleting them from the nodes.

## USAGE 
_________________

### The Peer:

*Usage:* 

To join the CHORD ring, the following commands are used:

1. For the first node joining the ring:
   ```bash
   python3 HandleNode.py <port_number>
   ```
   Here, `port_number` is the port at which the node will listen for requests.

2. For any forthcoming nodes into the ring:
   ```bash
   python3 HandleNode.py <port_number_of_new_node> <port_number_of_existing_node>
   ```
   Here, `port_number_of_new_node` is the port at which the new node will listen for requests, and `port_number_of_existing_node` is the port number of any of the other pre-existing nodes in the ring.

### The Client:

*Usage:* `python3 client.py`

The client program operates through a menu-driven interface. It requires the user to input the port number of the node to which the client wants to connect. The client can then select an option from the menu for tasks such as insert, search, delete, and so on.
