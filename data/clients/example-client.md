# Example Client - Retail Co

## Overview
Example Client is a mid-size retail company with 50+ physical stores undergoing digital transformation. They're modernizing their e-commerce platform to support omnichannel retail and improve customer experience.

## Key Stakeholders
- **Jane Doe** (Product Owner) - jane.doe@example-client.example
  - Primary decision maker for feature priorities
  - Weekly sync on Tuesdays at 10am
- **John Smith** (Engineering Lead) - john.smith@example-client.example
  - Technical point of contact
  - Reviews all architecture decisions
- **Mary Johnson** (VP of Digital) - mary.johnson@example-client.example
  - Executive sponsor
  - Monthly status updates

## Technical Context

### Current State
- Legacy Java monolith (10+ years old)
- Oracle database with complex stored procedures
- jQuery-based frontend
- On-premise hosting

### Target State
- Microservices architecture with Node.js
- PostgreSQL database
- React frontend with Next.js
- AWS cloud infrastructure

### Integration Points
- POS system (real-time inventory sync)
- ERP system (SAP)
- Payment gateway (Stripe)
- Shipping providers (FedEx, UPS APIs)

## Communication Preferences
- Slack channel: #acme-example-client
- Weekly status meetings: Tuesday 10am ET
- Emergency contact: On-call rotation in PagerDuty

## Important Notes
- PCI compliance required for payment handling
- Data must remain in US regions
- 99.9% uptime SLA for production systems
