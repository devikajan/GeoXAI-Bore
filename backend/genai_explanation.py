import ollama


def generate_explanation(
    failure_probability,
    risk_category,
    top_features
):
    """
    Generate a natural-language borewell risk explanation
    using a local Llama 3.2 model through Ollama.
    """

    probability = failure_probability * 100

    feature_text = ""

    for item in top_features[:5]:
        feature_text += (
            f"- Feature: {item['feature']}\n"
            f"  SHAP value: {item['shap_value']}\n"
            f"  Impact: {item['impact']}\n"
        )

    prompt = f"""
You are the Generative AI explanation component of the
GeoXAI-Bore borewell failure prediction system.

Your task is to explain an ML prediction using ONLY the
provided prediction and SHAP information.

Borewell failure probability in the next 6 months:
{probability:.2f}%

Risk category:
{risk_category}

SHAP-based factors:
{feature_text}

Write a clear explanation for a non-technical user.

Include:
1. Overall risk and probability.
2. The most important factors.
3. Which factors increase or decrease predicted failure risk.
4. One practical recommendation.

Do not invent measurements, causes, or facts that are not provided.
Do not claim that a factor physically causes failure just because
SHAP shows model influence.

Keep the response under 150 words.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]