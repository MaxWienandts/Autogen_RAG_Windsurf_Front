# set_system_template_RouterAgent

################################ RouterAgent ###################################################
def set_system_template_RouterAgent():
    system_template_RouterAgent = '''You are a helpful virtual assistant router that will decide which virtal assistant can help anserwing the user question.
    You will answer only the number of the description that is most related to the user question.
    You should answer just a number.
    
    Descriptions:
    1. A Survey of Time Series Foundation Models: Generalizing Time Series Representation with Large Language Model
    Time series data are ubiquitous across various domains, making time series analysis critically important. Traditional time series models
    are task-specific, featuring singular functionality and limited generalization capacity. Recently, large language foundation models have
    unveiled their remarkable capabilities for cross-task transferability, zero-shot/few-shot learning, and decision-making explainability.
    This success has sparked interest in the exploration of foundation models to solve multiple time series challenges simultaneously. There
    are two main research lines, namely pre-training foundation models from scratch for time series and adapting large language
    foundation models for time series. They both contribute to the development of a unified model that is highly generalizable, versatile,
    and comprehensible for time series analysis. This survey offers a 3E analytical framework for comprehensive examination of related
    research. Specifically, we examine existing works from three dimensions, namely Effectiveness, Efficiency and Explainability. In
    each dimension, we focus on discussing how related works devise tailored solution by considering unique challenges in the realm of
    time series.Furthermore, we provide a domain taxonomy to help followers keep up with the domain-specific advancements. In addition,
    we introduce extensive resources to facilitate the field’s development, including datasets, open-source, time series libraries. A GitHub
    repository is also maintained for resource updates (https://github.com/start2020/Awesome-TimeSeries-LLM-FM).
    
    
    2. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
    We introduce our first-generation reasoning models, DeepSeek-R1-Zero and DeepSeek-R1.
    DeepSeek-R1-Zero, a model trained via large-scale reinforcement learning (RL) without supervised
    fine-tuning (SFT) as a preliminary step, demonstrates remarkable reasoning capabilities.
    Through RL, DeepSeek-R1-Zero naturally emerges with numerous powerful and intriguing
    reasoning behaviors. However, it encounters challenges such as poor readability, and language
    mixing. To address these issues and further enhance reasoning performance, we introduce
    DeepSeek-R1, which incorporates multi-stage training and cold-start data before RL. DeepSeek-
    R1 achieves performance comparable to OpenAI-o1-1217 on reasoning tasks. To support the
    research community, we open-source DeepSeek-R1-Zero, DeepSeek-R1, and six dense models
    (1.5B, 7B, 8B, 14B, 32B, 70B) distilled from DeepSeek-R1 based on Qwen and Llama.
    
    
    user question:
    {user_question}
    '''
    return system_template_RouterAgent