# Physical Layer in System Design

## 1. Fundamentals of the Physical Layer

The Physical Layer forms the foundational level (Layer 1) of the OSI Reference Model, responsible for the transmission and reception of raw bit streams over a physical transmission medium.

### Core Functions
- **Bit Transmission**: Converts data bits into physical signals
- **Physical Medium Handling**: Manages the interface with transmission media
- **Signal Encoding**: Converts binary data into signals suitable for transmission
- **Transmission Rate Control**: Regulates data transmission speeds
- **Physical Topology Definition**: Determines how devices connect physically

### Key Characteristics
- Deals with mechanical, electrical, functional, and procedural aspects
- Hardware-oriented layer interfacing directly with transmission media
- Concerned with raw bits rather than logical data structures
- Provides physical medium activation, maintenance, and deactivation

## 2. Transmission Media Types

### Guided Media (Wired)
- **Twisted Pair Cable**
  - UTP (Unshielded Twisted Pair): Categories 3, 5, 5e, 6, 6a, 8
  - STP (Shielded Twisted Pair): Provides better protection against EMI
  - Performance metrics: Attenuation, cross-talk, impedance

- **Coaxial Cable**
  - Baseband coaxial: Single channel digital transmission
  - Broadband coaxial: Multiple channel analog transmission
  - Key parameters: Core diameter, shielding effectiveness, impedance (typically 50Ω or 75Ω)

- **Fiber Optic Cable**
  - **Single-mode**: Narrow core (8-10μm), long-distance transmission up to 100km+
  - **Multi-mode**: Larger core (50-62.5μm), shorter distances up to 2km
  - Transmission techniques: Total internal reflection
  - Advantages: High bandwidth, immunity to EMI, low signal attenuation

### Unguided Media (Wireless)
- **Radio Frequency**
  - Frequency ranges: VLF, LF, MF, HF, VHF, UHF, SHF, EHF
  - Applications: Wi-Fi, cellular networks, Bluetooth, IoT communications

- **Microwave**
  - Terrestrial microwave: Point-to-point communication
  - Satellite microwave: Global coverage capabilities
  - Frequency bands: C-band, Ku-band, Ka-band

- **Infrared**
  - Line-of-sight transmission requirements
  - Short-range applications like remote controls and IrDA devices

## 3. Signal Encoding Techniques

### Digital-to-Digital Encoding
- **NRZ (Non-Return to Zero)**
  - NRZ-L: Voltage level determines bit value
  - NRZ-I: Transition or lack thereof determines bit value
  - Limitations: Clock recovery issues, DC bias

- **Manchester Encoding**
  - Self-clocking mechanism with mid-bit transition
  - Transition from high-to-low represents 0, low-to-high represents 1
  - Used in Ethernet (IEEE 802.3)

- **Differential Manchester**
  - Transition at beginning of each bit period
  - Presence/absence of mid-bit transition determines bit value
  - Used in Token Ring networks

- **AMI (Alternate Mark Inversion)**
  - Three voltage levels: positive, negative, and zero
  - Zeros represented by absence of signal (0V)
  - Ones alternating between positive and negative voltages

### Digital-to-Analog Modulation
- **Amplitude Shift Keying (ASK)**
  - Varies signal amplitude to represent digital data
  - Susceptible to noise interference

- **Frequency Shift Keying (FSK)**
  - Different frequencies represent different bit values
  - More noise-resistant than ASK

- **Phase Shift Keying (PSK)**
  - Varies signal phase to encode data
  - BPSK, QPSK, 8-PSK variants increasing data rate

- **Quadrature Amplitude Modulation (QAM)**
  - Combines amplitude and phase modulation
  - 16-QAM, 64-QAM, 256-QAM offering higher data rates

## 4. Multiplexing Techniques

### Frequency Division Multiplexing (FDM)
- Divides available bandwidth into non-overlapping frequency bands
- Each channel occupies different frequency range
- Used in radio broadcasting, cable TV

### Time Division Multiplexing (TDM)
- Divides signal into time slots, one for each channel
- Synchronous TDM: Fixed allocation of time slots
- Statistical TDM: Dynamic allocation based on demand
- Applications: T1/E1 lines, SONET/SDH

### Wavelength Division Multiplexing (WDM)
- Multiple optical signals on single fiber using different wavelengths
- CWDM (Coarse WDM): Fewer channels with wider spacing
- DWDM (Dense WDM): Many channels with narrow spacing
- Enables terabit capacity on single fiber

### Code Division Multiplexing (CDM)
- Uses unique codes to separate channels
- CDMA implementation in mobile networks
- Allows multiple transmitters to share frequency band simultaneously

## 5. Physical Layer Devices

### Network Interface Cards (NICs)
- Physical layer interface between computer and network
- Handles media access control and physical encoding
- Implements PHY (physical layer transceiver) functionality

### Repeaters
- Regenerates signal to extend transmission distance
- Operates at bit level without protocol awareness
- Combats signal attenuation issues

### Hubs
- Multi-port repeaters broadcasting to all connected devices
- Types: Passive, active, intelligent, and switching
- Limited to half-duplex operation

### Media Converters
- Converts between different physical media types
- Example: Twisted pair to fiber optic conversion
- Enables mixed-media networks

## 6. Physical Layer Standards and Protocols

### Ethernet Physical Layer Standards
- **10BASE-T**: 10 Mbps over twisted pair (IEEE 802.3i)
- **100BASE-TX**: 100 Mbps Fast Ethernet (IEEE 802.3u)
- **1000BASE-T**: 1 Gbps over copper (IEEE 802.3ab)
- **10GBASE-T**: 10 Gbps over copper (IEEE 802.3an)
- **40/100GBASE-T**: 40/100 Gbps standards

### Wireless Standards Physical Layer
- **IEEE 802.11**: Wi-Fi family physical layer specifications
  - 802.11a/b/g/n/ac/ax with different modulation schemes
  - Channel access methods: DSSS, OFDM, MIMO-OFDM
- **IEEE 802.15**: Bluetooth, ZigBee physical layers
- **IEEE 802.16**: WiMAX physical layer specifications

### Telecommunications Standards
- **SONET/SDH**: Synchronous optical fiber transmission
- **DSL**: Digital Subscriber Line variants (ADSL, VDSL)
- **DOCSIS**: Data Over Cable Service Interface Specification

## 7. Physical Layer Design Considerations

### Signal Integrity
- **Attenuation**: Signal power loss over distance
- **Noise**: Thermal, impulse, crosstalk interference
- **Jitter**: Timing variations in signal transitions
- **Impedance Matching**: Preventing signal reflections
- **EMI/RFI**: Electromagnetic and radio frequency interference

### Performance Metrics
- **Bit Rate**: Raw transmission speed in bits per second
- **Baud Rate**: Signal changes per second
- **Bandwidth**: Frequency range available for transmission
- **Throughput**: Actual usable data rate
- **Bit Error Rate (BER)**: Errors per transmitted bits
- **Signal-to-Noise Ratio (SNR)**: Signal strength vs. noise

### Distance Limitations
- Cable length restrictions for different media types
- Signal regeneration requirements
- Latency considerations over distance

## 8. Error Detection at Physical Layer

### Parity Checking
- Even parity: Total number of 1s is even
- Odd parity: Total number of 1s is odd
- Limited to single-bit error detection

### Cyclic Redundancy Check (CRC)
- Polynomial division-based error detection
- Highly effective for burst errors
- Implemented in hardware for real-time operation

### Error Correction Techniques
- Forward Error Correction (FEC)
- Hamming codes, Reed-Solomon codes
- Trade-off between overhead and correction capability

## 9. Modern Physical Layer Technologies

### High-Speed Serial Interfaces
- **PCI Express**: Serial expansion bus standard
- **USB**: Universal Serial Bus physical layer specifications
- **Thunderbolt**: Combined PCI Express and DisplayPort

### Optical Transport Networks
- **Coherent Optics**: Advanced modulation for 100G+ networks
- **Silicon Photonics**: Integrated optical circuits
- **Optical Switching**: All-optical network designs

### Low-Power Physical Layers
- **IoT-specific PHYs**: Bluetooth LE, IEEE 802.15.4
- **LPWAN technologies**: LoRa, SigFox, NB-IoT physical layers
- **Energy harvesting considerations**: Ultra-low power design

## 10. Physical Layer Security Considerations

### Tap Detection
- Monitoring for unauthorized physical connections
- Fiber optic intrusion detection systems
- Cable shielding and physical security

### Jamming Resistance
- Spread spectrum techniques (FHSS, DSSS)
- Adaptive frequency hopping
- Signal power management

### Hardware Security
- Tamper-evident/resistant device design
- Physical layer encryption capabilities
- Quantum cryptography at physical layer