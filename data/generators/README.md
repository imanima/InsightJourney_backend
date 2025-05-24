# Test Data Generator for Coaching/Therapy Conversations

This module generates realistic coaching and therapy session transcripts using OpenAI's GPT-4 model. It creates natural, contextually appropriate conversations between clients and professionals based on detailed personas and session themes.

## Project Structure

```
test_data_generator/
├── config/
│   ├── clients.py         # Client personas and profiles
│   ├── professionals.py   # Professional (coach/therapist) personas
│   └── session_themes.py  # Session themes and progression
├── scripts/
│   └── generate_conversations.py  # Main conversation generator
├── output/               # Generated conversation transcripts
└── requirements.txt      # Project dependencies
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Configure personas and themes:
   - Edit `config/clients.py` to add or modify client personas
   - Edit `config/professionals.py` to add or modify professional personas
   - Edit `config/session_themes.py` to customize session themes and progression

2. Generate conversations:
```bash
python scripts/generate_conversations.py
```

The script will generate a series of conversations between the specified client and professional, following the defined session progression. Each conversation will be saved as a text file in the `output` directory.

## Customization

### Client Personas
Client personas are organized by type (e.g., tech_professionals, students) and include:
- Basic information (name, age, role)
- Background and experience
- Tech habits and preferences
- Current challenges and goals
- Personality traits

### Professional Personas
Professional personas include:
- Basic information and credentials
- Background and expertise
- Coaching/therapy style
- Strengths and techniques
- Technology usage

### Session Themes
Session themes are organized by client type and include:
- Specific topics to cover
- Techniques to use
- Expected outcomes
- Session progression (initial assessment, core work, integration, closure)

## Output Format

Generated conversations are saved as text files with the following format:
```
Session [number]
Date: [timestamp]
Client: [name] ([role])
Professional: [name] ([role])

[Conversation transcript with timestamps and speaker identification]
```

## Example

To generate conversations for Alex (tech professional) with Dr. Harper:
```python
generator = ConversationGenerator()
generator.generate_all_sessions(
    client_key="alex_designer",
    professional_key="dr_harper",
    client_type="tech_professionals",
    theme_key="imposter_syndrome"
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 