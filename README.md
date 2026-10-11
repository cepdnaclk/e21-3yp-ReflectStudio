<div align="center">

# ReflectCare
### AI-Enabled Smart Mirror for Assisted Living and Family Connectivity

**Originally developed as ReflectStudio**  
**Third-Year Computer Engineering Group Project | University of Peradeniya, Sri Lanka**

[Project Repository](https://github.com/sithum0430/e21-3yp-ReflectStudio) · [Source Code](./mirrorManwithUI) · [Mobile App](./mobile_app) · [Documentation](./docs)

</div>

---

## Overview

ReflectCare (originally **ReflectStudio**) is an AI- and IoT-enabled smart mirror designed to make everyday information and assisted-care interactions more accessible. The system combines an interactive mirror display, camera-based sensing, voice interaction, environmental monitoring, cloud-connected services, and a companion mobile application.

Its assisted-living use case focuses on helping older adults access useful daily information while making it easier for family members or caregivers to share reminders and stay connected. ReflectCare is an **assistive prototype**, not a medical device or substitute for professional care.

## The Problem

Conventional mirrors provide no contextual information or interaction. Meanwhile, some older adults can find phone-centric interfaces inconvenient for accessing daily information or communicating with caregivers. ReflectCare explores a familiar, hands-free interface that brings selected information and family interactions into a device already used in everyday routines.

## Key Capabilities

| Capability | What it does |
| --- | --- |
| Smart mirror dashboard | Presents useful information such as time, date, weather, and personalized content on the mirror display. |
| Voice interaction | Supports hands-free commands and an interactive on-screen assistant/avatar. |
| Presence awareness | Uses sensing hardware to detect a person near the mirror and trigger configured interactions. |
| Facial analysis and personalization | Uses camera-based computer vision for user-aware features; exact recognition functionality depends on the enabled configuration. |
| Emotion-aware assistance | Explores emotion recognition and caregiver notifications; outputs are estimates, not diagnoses. |
| Family connectivity | Allows authorized family members/caregivers to share photos, messages, or reminders through the companion app and connected services. |
| Environmental awareness | Integrates sensors and weather data to provide context-aware information. |
| Connected device control | Supports connected outputs such as LED lighting and other configured actuators. |
| Music and daily services | Integrates selected media and information services for everyday convenience. |

> **Implementation note:** The repository includes multiple experimental and evolving configurations. Availability of individual features depends on the hardware attached, cloud configuration, and software version being run.

## System Architecture

```text
                  Family / Caregiver
                  Flutter Mobile App
                          |
                     Cloud Services
                   (AWS / APIs / data)
                          |
                         Wi-Fi
                          |
          +---------------v----------------+
          |      Raspberry Pi Mirror       |
          |                                |
          |  Smart Mirror UI               |
          |  Voice / Avatar Interaction    |
          |  Computer Vision / AI          |
          |  Weather and Daily Services    |
          |  Cloud Communication           |
          +---+----------+------------+----+
              |          |            |
         Camera/Mic   Display      ESP32 / Sensors
                                    |
                              LEDs / Actuators
```

**Typical data flow:** A sensor or user interaction is processed by the Raspberry Pi; the mirror updates the display or interacts with an external service. Family-shared content travels through configured cloud services to the mirror. Device-control signals travel through the connected microcontroller or interface.

## Technology Stack

| Layer | Technologies / Components |
| --- | --- |
| Edge computing | Raspberry Pi, Raspberry Pi OS |
| Embedded control | ESP32 and connected sensors/actuators |
| Application logic | Python |
| User interface | Browser-based HTML/CSS/JavaScript components and mirror application modules |
| Computer vision | Camera input, OpenCV and project-specific AI/ML components |
| Companion application | Flutter / Dart |
| Cloud and storage | AWS services (including S3 and Rekognition where configured); other backend services depend on the module |
| Communication | Wi-Fi, HTTP APIs, WebSocket/serial connections where implemented |
| External data | Weather API and other configured third-party services |
| Development tools | Git, GitHub, VS Code |

The actual Python packages, Flutter packages, SDK versions, API providers, and cloud resources should be verified against the current code and configuration before deployment.

## Hardware

The system is built around a display behind mirror glass, a Raspberry Pi, and connected peripheral devices.

- Raspberry Pi (the public repository documents a Raspberry Pi 4 Model B configuration)
- Display panel or monitor and two-way mirror glass
- Camera module / USB camera (depending on the build)
- Microphone and speakers
- ESP32 microcontroller
- Presence and environmental sensors (varies by prototype; repository documentation references radar, BME280, OPT3001, and camera sensing)
- LED strip, relay/fan or other connected actuators where installed
- Power supplies, wiring, and suitable physical enclosure

**Hardware configurations have evolved during development.** Check the selected branch and hardware integration code before wiring devices. Never connect high-voltage loads without correctly rated isolation and electrical protection.

## Repository Structure

The public repository currently contains the following top-level entries:

```text
e21-3yp-ReflectStudio/
├── code/               # Additional project code
├── docs/               # Project documentation and supporting material
├── mirrorManwithUI/    # Raspberry Pi mirror application and UI
├── mobile_app/         # Flutter companion application
├── rpi_mirrorman/      # Raspberry Pi / mirror-man related implementation
└── README.md           # Project overview and setup guide
```

Some development artifacts and generated files may also be present. The exact contents of each folder may change across branches.

## Getting Started

### 1. Prerequisites

- A Raspberry Pi with a compatible Raspberry Pi OS installation, connected to a display
- Python 3 and `venv`
- Git
- A microphone, speakers, and camera for their respective features
- An ESP32 and relevant sensors for embedded integrations
- Flutter SDK and a supported Android development environment if building the mobile app
- Internet connection and configured third-party accounts/API credentials for online features

### 2. Clone the project

```bash
git clone https://github.com/sithum0430/e21-3yp-ReflectStudio.git
cd e21-3yp-ReflectStudio
```

### 3. Prepare the mirror application

```bash
cd mirrorManwithUI
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies from the appropriate requirements file **if one is included in the selected application folder**:

```bash
# Example: run only if requirements.txt exists here
python -m pip install -r requirements.txt
```

If the application uses a different dependency file or multiple modules, follow their individual dependency definitions. A universal one-command launcher has **not been verified** for every repository configuration.

### 4. Configure services and hardware

1. Configure camera, microphone, speakers, and display in Raspberry Pi OS.
2. Attach the ESP32 and sensors according to the pin mappings used by the chosen firmware.
3. Set up required cloud resources and permissions for family communication and image sharing.
4. Provide weather and other third-party API credentials through the application's supported configuration mechanism.
5. Verify local connectivity between the Raspberry Pi and ESP32, and internet access for online modules.

**Security:** Never put AWS keys, API keys, passwords, face embeddings, private family photos, or other sensitive data in the repository. Use local configuration or environment variables that are excluded from Git.

### 5. Run the mirror

The integrated mirror may require several independently started components, such as:

- Mirror UI
- Vision / computer-vision engine
- Serial or ESP32 communication bridge
- Voice/assistant services

Locate the corresponding application entry points or launch scripts in the selected branch and start them in the order required by that configuration. Check that the display and peripheral devices are detected before testing full integration.

> **To make this fully reproducible:** Add the exact launch commands, supported OS/Python versions, environment-variable names, and a verified wiring table after checking the version of the repository you intend to present.

### 6. Set up the Flutter app

```bash
cd ../mobile_app
flutter pub get
flutter run
```

The Flutter project directory containing `pubspec.yaml` may be nested inside `mobile_app`; if so, change into that directory first. Configure the backend/cloud endpoint and any platform permissions required by the app before launching.

## Demonstration Workflow

1. A user approaches the smart mirror; configured presence sensing detects activity.
2. The mirror dashboard displays information such as time and weather.
3. The user interacts through a wake phrase and voice commands where configured.
4. Camera-based processing can support user-aware interactions and emotion-aware prototypes.
5. An authorized family member sends a photo, message, or reminder through the mobile app.
6. The cloud-connected mirror receives and presents the shared content.

This sequence describes the intended integrated experience; demonstrations should identify which features are enabled in the specific build.

## Privacy, Responsible AI, and Data Handling

ReflectCare may process facial imagery, voice input, caregiver messages, photos, and profile information. Deployments involving real people should obtain appropriate consent and implement access controls, transport security, data minimization, retention limits, and deletion procedures.

- Emotion predictions are probabilistic observations, **not clinical assessments**.
- Camera and microphone usage should be transparent to users.
- Family photos and messages must be accessible only to authorized users.
- Credentials and private data must be excluded from public commits.
- Cloud security settings and data-retention behavior must be verified before real-world use.

## Project Origins and Attribution

ReflectCare is the assisted-care-focused presentation of **ReflectStudio**, a third-year Computer Engineering group project at the **University of Peradeniya**. The project brings together original integration work and pre-existing hardware platforms, software frameworks, libraries, and external services. Third-party components retain their own licenses and attribution requirements.

## Team

- Anna Kurera
- Sithum Perera
- Thenuka Ravindu
- Kasun Lakshan

**Department of Computer Engineering — University of Peradeniya, Sri Lanka**

## Development Status

**Academic prototype / ongoing development.** The codebase contains features and experimental integrations developed across multiple branches and hardware configurations. Feature availability, system setup, and deployment readiness may vary between versions.

## License

Consult the repository's license file, if present, and the individual licenses of third-party dependencies. No license is implied by this README alone.

---

<div align="center">

**ReflectCare — Making everyday care and connection part of a familiar reflection.**

</div>
