import os


def generate_claude(prompt: str) -> str:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_openai(prompt: str) -> str:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Add it to your .env file.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate(prompt: str, backend: str) -> str:
    if backend == "openai":
        return generate_openai(prompt)
    return generate_claude(prompt)
