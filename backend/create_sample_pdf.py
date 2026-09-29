"""
Generates a realistic multi-page PDF document about Computer Networks.
This provides a ready-made PDF file for hackathon judges and testers.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_sample_pdf(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )

    story = []

    # Cover / Page 1
    story.append(Paragraph("Computer Networks & Communications", title_style))
    story.append(Paragraph("<b>Course Code:</b> CS-401 &bull; <b>Academic Year:</b> 2026", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Overview:</b> Computer networks allow multiple autonomous computing devices to interconnect, share computational resources, exchange messages, and route packets across geographical distances. This syllabus review manual covers the fundamental architectural models, hardware systems, topologies, and core protocols that underpin the modern global Internet.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Topic 1: The OSI Reference Model", h2_style))
    story.append(Paragraph("The Open Systems Interconnection (OSI) reference model was formulated by the International Organization for Standardization (ISO) to establish an open vendor-neutral architecture. It structures network operations into 7 discrete, hierarchical layers:", body_style))
    story.append(Paragraph("<b>1. Physical Layer:</b> Deals with raw bit stream transmission over physical media (twisted pair copper cables, fiber optic glass, radio frequency waves). Regulates voltage levels, pinouts, and bit timing.", body_style))
    story.append(Paragraph("<b>2. Data Link Layer:</b> Handles node-to-node framing, physical hardware MAC addressing (Media Access Control), error detection via Cyclic Redundancy Checks (CRC), and flow control across a single local link.", body_style))
    story.append(Paragraph("<b>3. Network Layer:</b> The core routing layer. Manages logical IP addressing, subnetting, packet forwarding across intermediate routers, and path determination algorithms (Dijkstra SPF, Bellman-Ford).", body_style))
    story.append(Paragraph("<b>4. Transport Layer:</b> Provides transparent end-to-end process-to-process communication. Implements segmentation, port multiplexing, and reliability controls (TCP connection handshakes vs UDP best-effort).", body_style))
    story.append(Paragraph("<b>5. Session Layer:</b> Establishes, maintains, and synchronizes dialogue sessions between active client/server applications.", body_style))
    story.append(Paragraph("<b>6. Presentation Layer:</b> Synthesizes data syntax, character code translations (ASCII, UTF-8), cryptographic encryption (TLS/SSL), and compression algorithms.", body_style))
    story.append(Paragraph("<b>7. Application Layer:</b> Closest layer to the end user. Contains high-level network protocols such as HTTP, DNS, SMTP, SSH, and FTP.", body_style))
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("Topic 2: TCP/IP Protocol Architecture", h2_style))
    story.append(Paragraph("While the OSI model serves primarily as a theoretical blueprint, the Transmission Control Protocol / Internet Protocol (TCP/IP) suite is the pragmatic, battle-tested standard of the global Internet. It condenses network functionality into four robust layers:", body_style))
    story.append(Paragraph("<b>1. Network Access (Link) Layer:</b> Combines the physical and data link functions. Encapsulates IP datagrams into Ethernet or Wi-Fi frames, handling hardware transmission.", body_style))
    story.append(Paragraph("<b>2. Internet Layer:</b> Centered on the Internet Protocol (IPv4 and IPv6). Datagrams are routed independently across diverse interconnected networks. Includes auxiliary protocols like ICMP (for ping/diagnostics) and IGMP.", body_style))
    story.append(Paragraph("<b>3. Transport Layer:</b> Features two primary protocols. TCP (Transmission Control Protocol) is connection-oriented, delivering reliable byte streams through three-way handshake (SYN, SYN-ACK, ACK), sliding window flow control, and sequence retransmissions. Conversely, UDP (User Datagram Protocol) is lightweight, connectionless, and unacknowledged, ideal for real-time multiplayer gaming, VoIP, and DNS queries where low latency takes precedence over lossless retransmission.", body_style))
    story.append(Paragraph("<b>4. Application Layer:</b> Directly hosts application-level services like HTTP/HTTPS on port 80/443, DNS on UDP/TCP port 53, SMTP on port 25, and SSH on port 22.", body_style))
    story.append(PageBreak())

    # Page 3
    story.append(Paragraph("Topic 3: Network Devices and Infrastructure", h2_style))
    story.append(Paragraph("Building modern enterprise networks requires deploying specialized intermediate hardware appliances across corresponding OSI layers:", body_style))
    story.append(Paragraph("<b>1. Repeaters & Hubs (Layer 1):</b> Basic electrical signal regenerators. Hubs indiscriminately broadcast incoming electrical pulses to every other port, creating a unified collision domain that degrades bandwidth efficiency.", body_style))
    story.append(Paragraph("<b>2. Bridges & Switches (Layer 2):</b> Intelligent multiport bridge devices. Modern Ethernet switches inspect source and destination MAC addresses within incoming frames, populating Content Addressable Memory (CAM) tables to forward frames solely to the intended target port, eliminating collisions.", body_style))
    story.append(Paragraph("<b>3. Routers (Layer 3):</b> Network layer appliances equipped with routing tables and routing algorithms (OSPF, BGP, RIP). Routers connect distinct broadcast domains and logical subnets, directing IP packets along optimal paths across public and private backbones.", body_style))
    story.append(Paragraph("<b>4. Firewalls & Gateways:</b> Stateful packet filters and deep packet inspection firewalls operate across Layers 3 through 7. Gateways translate heterogeneous communication protocols, such as interfacing VoIP telephony with traditional PSTN networks.", body_style))
    story.append(PageBreak())

    # Page 4
    story.append(Paragraph("Topic 4: Network Topologies", h2_style))
    story.append(Paragraph("A network topology describes the geometric arrangement of nodes, links, and peripherals:", body_style))
    story.append(Paragraph("<b>1. Star Topology:</b> Every workstation or server is cabled directly into a central switch. Easy to install, isolate faults, and expand. If one cable fails, only that workstation loses connection. However, the central switch represents a single point of failure.", body_style))
    story.append(Paragraph("<b>2. Mesh Topology:</b> Nodes possess redundant point-to-point connections with neighboring devices. In Full Mesh networks, n nodes require n*(n-1)/2 physical channels. Mesh topologies provide exceptional fault tolerance and resilience, making them the standard for core telecommunication backbones.", body_style))
    story.append(Paragraph("<b>3. Bus Topology:</b> All nodes share a common single coaxial backbone cable terminated with resistors. Economical for legacy environments, but a single cable break disables communication for the entire segment.", body_style))
    story.append(Paragraph("<b>4. Ring & Hybrid Topologies:</b> In a Ring, devices are arranged sequentially in a circle with token passing. Hybrid topologies combine Star and Bus or Star and Ring to balance cost and fault tolerance in campus environments.", body_style))
    story.append(PageBreak())

    # Page 5
    story.append(Paragraph("Topic 5: Core Protocols & Network Security", h2_style))
    story.append(Paragraph("Standardized network protocols govern how data is addressed, routed, and secured:", body_style))
    story.append(Paragraph("<b>1. Domain Name System (DNS):</b> The phonebook of the Internet. Resolves alphabetic names (e.g., example.edu) to 32-bit IPv4 or 128-bit IPv6 addresses via root, top-level domain (TLD), and authoritative name servers.", body_style))
    story.append(Paragraph("<b>2. Dynamic Host Configuration Protocol (DHCP):</b> Eliminates manual network configuration by automatically leasing IP addresses, default gateway pointers, and subnet masks to new devices through the DORA exchange (Discover, Offer, Request, Acknowledge).", body_style))
    story.append(Paragraph("<b>3. Address Resolution Protocol (ARP):</b> Resolves known Layer 3 IP addresses to physical Layer 2 MAC addresses on local subnets.", body_style))
    story.append(Paragraph("<b>4. HTTP & HTTPS:</b> The foundation of the World Wide Web. HTTPS integrates Transport Layer Security (TLS) cryptographic handshakes to encrypt payload data against man-in-the-middle eavesdropping.", body_style))
    story.append(Paragraph("<b>5. Internet Control Message Protocol (ICMP):</b> Used by system administrators and diagnostic utilities (such as ping and traceroute) to monitor latency, TTL expiry, and network unreachability.", body_style))

    doc.build(story)
    print(f"Sample PDF generated successfully at: {output_path}")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "sample_docs")
    target = os.path.join(out_dir, "Computer_Networks.pdf")
    create_sample_pdf(target)
