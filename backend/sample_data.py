"""
Sample data and sample PDF generator for StudyFlow AI.
Allows instant testing and demonstration during college hackathons.
"""
import io
from pypdf import PdfWriter


SAMPLE_DOCUMENT_NAME = "Computer_Networks_Fundamentals.pdf"

SAMPLE_TEXT_PAGES = [
    """CHAPTER 1: INTRODUCTION TO COMPUTER NETWORKS & OSI MODEL
Computer networks allow multiple computing devices to share data, hardware resources, and communications.
The Open Systems Interconnection (OSI) model is a conceptual framework that standardizes network communication into seven distinct layers:
1. Physical Layer: Responsible for electrical, optical, and radio frequency transmission of raw bit streams.
2. Data Link Layer: Provides node-to-node data transfer, MAC addressing, and frame error detection (e.g., Ethernet switches).
3. Network Layer: Responsible for packet routing across different networks, logical IP addressing, and path determination.
4. Transport Layer: Delivers end-to-end communication, flow control, reliability, and error checking using protocols like TCP and UDP.
5. Session Layer: Manages dialogues, sessions, and connections between cooperating applications.
6. Presentation Layer: Handles data translation, character encoding, compression, and SSL/TLS encryption.
7. Application Layer: Interacts directly with software applications, containing protocols like HTTP, DNS, SMTP, and FTP.""",

    """CHAPTER 2: THE TCP/IP PROTOCOL SUITE
The TCP/IP model is the foundational architecture of the modern Internet, consisting of four functional layers:
- Network Access Layer (Link Layer): Maps to OSI Physical and Data Link layers, handling hardware frames and ARP.
- Internet Layer: Handles IP addressing (IPv4, IPv6) and routing protocols like ICMP, OSPF, and BGP.
- Transport Layer: Includes Transmission Control Protocol (TCP) for connection-oriented, reliable three-way handshake delivery, and User Datagram Protocol (UDP) for low-latency, connectionless streaming.
- Application Layer: Encompasses high-level user services including Web (HTTP/HTTPS), Email (SMTP/IMAP), File Transfer (FTP), and Domain Name Resolution (DNS).
Key differences: While OSI is a strict theoretical 7-layer reference model, TCP/IP is a practical, widely deployed 4-layer protocol stack.""",

    """CHAPTER 3: NETWORK DEVICES AND HARDWARE
Computer networks rely on specialized intermediate hardware devices to transmit data packets:
1. Hubs: Layer 1 physical devices that broadcast incoming electrical signals to all connected ports indiscriminately, creating collision domains.
2. Switches: Layer 2 devices that inspect MAC addresses in data link frames, maintaining a CAM table to intelligently forward frames only to the designated recipient port.
3. Routers: Layer 3 devices that inspect destination IP addresses in packet headers and use routing tables (dynamic protocols like OSPF, BGP, RIP) to forward packets across different subnets.
4. Gateways: Translators between disparate network architectures and protocols across higher OSI layers.
5. Firewalls: Security appliances operating at Layers 3 through 7 that inspect and filter packets based on predefined stateful rules and port security.""",

    """CHAPTER 4: NETWORK TOPOLOGIES
Network topology defines the physical or logical arrangement of computing nodes and communication links:
- Star Topology: All nodes are connected directly to a central hub or switch. If a single cable fails, only that device is affected. However, failure of the central switch disables the entire network segment.
- Mesh Topology: Every node is interconnected with redundant links (Full Mesh formula: n*(n-1)/2 links). Provides high fault tolerance and reliability at the cost of high cabling expense.
- Bus Topology: Nodes connect sequentially along a single common backbone cable terminated at both ends. Susceptible to collisions and line breaks.
- Ring Topology: Each device is connected to two neighbors forming a closed loop with unidirectional token passing.
- Hybrid Topology: Combines two or more distinct topologies (e.g., Star-Bus or Tree) to maximize scalability in enterprise networks.""",

    """CHAPTER 5: CORE NETWORK PROTOCOLS & SECURITY
Modern networking depends on standardized protocols governing specific communication workflows:
- DNS (Domain Name System): Resolves human-friendly domain names (e.g., google.com) into numerical IP addresses via hierarchical root, TLD, and authoritative nameservers over UDP port 53.
- DHCP (Dynamic Host Configuration Protocol): Automatically leases IP addresses, default gateways, and subnet masks to client devices using the DORA (Discover, Offer, Request, Acknowledge) process.
- HTTP and HTTPS: Hypertext Transfer Protocol operates on port 80; HTTPS provides encrypted cryptographic privacy via TLS/SSL certificates over port 443.
- ARP (Address Resolution Protocol): Resolves an IP address to a physical MAC address on local subnets.
- ICMP (Internet Control Message Protocol): Used for network diagnostics, error reporting, and latency measurement (e.g., ping and traceroute commands)."""
]

SAMPLE_TOPICS = [
    "OSI Model",
    "TCP/IP",
    "Network Devices",
    "Network Topologies",
    "Protocols"
]


def generate_sample_pdf_bytes() -> bytes:
    """
    Creates a valid sample PDF in memory using pypdf.
    """
    # Create empty PDF with metadata or text
    from pypdf import PdfWriter
    writer = PdfWriter()
    
    # We can create blank pages and set page text or create with basic canvas
    # Since pypdf is primarily a reader/manipulator, let's create pages with metadata
    for i, page_text in enumerate(SAMPLE_TEXT_PAGES):
        page = writer.add_blank_page(width=612, height=792)
        # Note: blank page in pypdf doesn't easily embed font streams without reportlab,
        # but our reader can also directly work with the sample text.
    
    output_stream = io.BytesIO()
    writer.write(output_stream)
    return output_stream.getvalue()
