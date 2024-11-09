# LogistiQ AI Negotiation Assistant

## Project Overview

LogistiQ is an AI-powered negotiation assistant designed for Gruber Logistics, developed for the Bolzano Hackathon 2024. This innovative system automates and streamlines the process of negotiating transportation services with suppliers, leveraging advanced language models and a sophisticated chat interface.

For more information about the Bolzano Hackathon 2024, visit: https://hackathon.bz.it/

## Key Features

- **Multi-lingual Support**: Capable of conducting negotiations in multiple languages, adapting to the supplier's preferred language.
- **Dynamic Pricing Strategy**: Implements a flexible negotiation strategy, starting from an initial price and gradually adjusting offers within a predefined range.
- **Real-time Web Interface**: Provides a user-friendly chat interface for human oversight and interaction during negotiations.
- **Integration with External Systems**: Designed to receive parameters from and return results to external logistics management systems.
- **Conversation Analysis**: Automatically extracts key information like final agreed prices from negotiation transcripts.

## Technical Stack

- **Backend**: Python with Flask web framework
- **AI Model**: Anthropic's Claude 3 Sonnet (via Amazon Bedrock)
- **LLM Framework**: LangChain for advanced language model interactions
- **Frontend**: HTML, JavaScript, and jQuery
- **API**: RESTful endpoints for starting chats and processing messages

## Setup and Installation

1. Clone the repository
2. Install required Python packages: `pip install -r requirements.txt`
3. Set up your AWS credentials for Bedrock access
4. Run the Flask application: `python app.py`

## Usage

1. The system can be initiated via API call to `/receive_params` with negotiation parameters
2. A local web interface will open automatically for monitoring and potential human intervention
3. The AI conducts the negotiation based on the provided parameters
4. Results are returned via API once the negotiation concludes

## Configuration

Key parameters that can be configured include:
- Starting price
- Maximum acceptable price
- Origin and destination cities
- Negotiation language

## Future Enhancements

- Integration with more language models and AI providers
- Enhanced analytics and reporting features
- Mobile app for on-the-go negotiation monitoring

## Contributing

We welcome contributions to improve LogistiQ. Please see our contributing guidelines for more information.

## License

This project is proprietary software owned by Gruber Logistics. All rights reserved.
