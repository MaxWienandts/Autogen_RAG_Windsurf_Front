import React, { useState, useEffect } from 'react';
import './Settings.css';

const DEFAULT_ROUTER_TEMPLATE = `You are a helpful virtual assistant router that will decide which virtal assistant can help anserwing the user question.
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
we introduce extensive resources to facilitate the field's development, including datasets, open-source, time series libraries. A GitHub
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
{user_question}`;

const DEFAULT_OUTER_TEMPLATE = `You are a helpful virtual assistant specialized in answering academic questions.
Your answers must be based on the context that you will receive.
You will answer considering the parameters:
- Target audience: {target_audience}
- Tone: {answer_tone}
- Length: {answer_length}

context:
{text_context}


User question:
{user_question}`;

const Settings = ({ onSave, settings: initialSettings }) => {
  const [activeTab, setActiveTab] = useState('response');
  const [settings, setSettings] = useState({
    // Response Settings
    target_audience: 'PhD student',
    answer_tone: 'Professional and Clear',
    answer_length: '4 paragraphs',
    
    // System Templates
    system_template_RouterAgent: DEFAULT_ROUTER_TEMPLATE,
    system_template_OuterAgent: DEFAULT_OUTER_TEMPLATE,
    
    // Environment Variables
    AZURE_ENDPOINT_LLM: '',
    DEPLOYMENT_NAME_LLM: '',
    API_VERSION: '',
    AZURE_OPENAI_API_KEY: '',
    EMBEDDING_KEY: '',
    AZURE_ENDPOINT_EMBEDDING: '',
    DEPLOYMENT_NAME_EMBEDDING: '',
    ELASTICSEARCH_ENDPOINT: '',
    ELASTICSEARCH_USER: '',
    ELASTICSEARCH_PASSWORD: '',
    ...initialSettings // This will override defaults if provided
  });

  const [saveStatus, setSaveStatus] = useState('');

  // Update local settings when initialSettings change, but preserve defaults if values are empty
  useEffect(() => {
    if (initialSettings) {
      setSettings(prev => ({
        ...prev,
        ...initialSettings,
        system_template_RouterAgent: initialSettings.system_template_RouterAgent || DEFAULT_ROUTER_TEMPLATE,
        system_template_OuterAgent: initialSettings.system_template_OuterAgent || DEFAULT_OUTER_TEMPLATE
      }));
    }
  }, [initialSettings]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = () => {
    onSave(settings);
    setSaveStatus('Settings saved successfully!');
    setTimeout(() => setSaveStatus(''), 3000); // Clear message after 3 seconds
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h2>Settings</h2>
      </div>
      
      <div className="settings-tabs">
        <button 
          className={`tab ${activeTab === 'response' ? 'active' : ''}`}
          onClick={() => setActiveTab('response')}
        >
          Response Settings
        </button>
        <button 
          className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          System Templates
        </button>
        <button 
          className={`tab ${activeTab === 'env' ? 'active' : ''}`}
          onClick={() => setActiveTab('env')}
        >
          Environment Variables
        </button>
      </div>

      <div className="settings-body">
        {activeTab === 'response' && (
          <div className="settings-section">
            <h3>Response Settings</h3>
            <div className="form-group">
              <label>Target Audience:</label>
              <input
                type="text"
                name="target_audience"
                value={settings.target_audience}
                onChange={handleChange}
                placeholder="e.g., PhD student"
              />
            </div>
            <div className="form-group">
              <label>Answer Tone:</label>
              <input
                type="text"
                name="answer_tone"
                value={settings.answer_tone}
                onChange={handleChange}
                placeholder="e.g., Professional and Clear"
              />
            </div>
            <div className="form-group">
              <label>Answer Length:</label>
              <input
                type="text"
                name="answer_length"
                value={settings.answer_length}
                onChange={handleChange}
                placeholder="e.g., 4 paragraphs"
              />
            </div>
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="settings-section">
            <h3>System Templates</h3>
            <div className="form-group">
              <label>Router Agent Template:</label>
              <div className="template-info">
                Available variables: {'{user_question}'}
              </div>
              <textarea
                name="system_template_RouterAgent"
                value={settings.system_template_RouterAgent}
                onChange={handleChange}
                rows={15}
                placeholder="Enter Router Agent template..."
              />
            </div>
            <div className="form-group">
              <label>Outer Agent Template:</label>
              <div className="template-info">
                Available variables: {'{target_audience}'}, {'{answer_tone}'}, {'{answer_length}'}, {'{text_context}'}, {'{user_question}'}
              </div>
              <textarea
                name="system_template_OuterAgent"
                value={settings.system_template_OuterAgent}
                onChange={handleChange}
                rows={10}
                placeholder="Enter Outer Agent template..."
              />
            </div>
          </div>
        )}

        {activeTab === 'env' && (
          <div className="settings-section">
            <h3>Environment Variables</h3>
            <div className="form-group">
              <label>Azure LLM Endpoint:</label>
              <input
                type="text"
                name="AZURE_ENDPOINT_LLM"
                value={settings.AZURE_ENDPOINT_LLM}
                onChange={handleChange}
                placeholder="Enter Azure LLM endpoint"
              />
            </div>
            <div className="form-group">
              <label>LLM Deployment Name:</label>
              <input
                type="text"
                name="DEPLOYMENT_NAME_LLM"
                value={settings.DEPLOYMENT_NAME_LLM}
                onChange={handleChange}
                placeholder="Enter deployment name"
              />
            </div>
            <div className="form-group">
              <label>API Version:</label>
              <input
                type="text"
                name="API_VERSION"
                value={settings.API_VERSION}
                onChange={handleChange}
                placeholder="Enter API version"
              />
            </div>
            <div className="form-group">
              <label>Azure OpenAI API Key:</label>
              <input
                type="password"
                name="AZURE_OPENAI_API_KEY"
                value={settings.AZURE_OPENAI_API_KEY}
                onChange={handleChange}
                placeholder="Enter Azure OpenAI API Key"
              />
            </div>
            <div className="form-group">
              <label>Azure Embedding Key:</label>
              <input
                type="password"
                name="EMBEDDING_KEY"
                value={settings.EMBEDDING_KEY}
                onChange={handleChange}
                placeholder="Enter Azure Embedding Key"
              />
            </div>
            <div className="form-group">
              <label>Azure Embedding Endpoint:</label>
              <input
                type="text"
                name="AZURE_ENDPOINT_EMBEDDING"
                value={settings.AZURE_ENDPOINT_EMBEDDING}
                onChange={handleChange}
                placeholder="Enter Azure Embedding endpoint"
              />
            </div>
            <div className="form-group">
              <label>Embedding Deployment Name:</label>
              <input
                type="text"
                name="DEPLOYMENT_NAME_EMBEDDING"
                value={settings.DEPLOYMENT_NAME_EMBEDDING}
                onChange={handleChange}
                placeholder="Enter embedding deployment name"
              />
            </div>
            <div className="form-group">
              <label>Elasticsearch Endpoint:</label>
              <input
                type="text"
                name="ELASTICSEARCH_ENDPOINT"
                value={settings.ELASTICSEARCH_ENDPOINT}
                onChange={handleChange}
                placeholder="Enter Elasticsearch endpoint"
              />
            </div>
            <div className="form-group">
              <label>Elasticsearch User:</label>
              <input
                type="text"
                name="ELASTICSEARCH_USER"
                value={settings.ELASTICSEARCH_USER}
                onChange={handleChange}
                placeholder="Enter Elasticsearch username"
              />
            </div>
            <div className="form-group">
              <label>Elasticsearch Password:</label>
              <input
                type="password"
                name="ELASTICSEARCH_PASSWORD"
                value={settings.ELASTICSEARCH_PASSWORD}
                onChange={handleChange}
                placeholder="Enter Elasticsearch password"
              />
            </div>
          </div>
        )}
      </div>

      <div className="settings-footer">
        <button className="save-button" onClick={handleSave}>Save Changes</button>
        {saveStatus && <span className="save-status">{saveStatus}</span>}
      </div>
    </div>
  );
};

export default Settings;
