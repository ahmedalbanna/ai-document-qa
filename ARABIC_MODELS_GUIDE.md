# Arabic Language Support - AI Document QA System

## 🌍 Multilingual Models Available

Your AI Document QA system now includes **intelligent Arabic language support** with multiple models optimized for different use cases.

---

## 📊 Available Models

### 1. **Aya (Recommended for Arabic)**
- **Size**: 4.8 GB
- **Languages**: 100+ languages including Arabic
- **Best for**: Arabic document analysis, questions, and answers
- **Features**:
  - Native Arabic language understanding
  - Professional Arabic writing
  - Cultural context awareness
  - Excellent for Arabic Q&A

### 2. **Llama 3.2 (Multilingual)**
- **Size**: 2.0 GB
- **Languages**: Multiple languages with improved Arabic support
- **Best for**: Mixed language documents
- **Features**:
  - Good Arabic comprehension
  - Faster inference than Aya
  - Better for code-switching content

### 3. **Llama 2 (Default)**
- **Size**: 3.8 GB
- **Languages**: Primarily English with limited Arabic
- **Best for**: English documents
- **Features**:
  - Fast and reliable
  - Best for English content

---

## 🚀 How to Use Arabic Models

### **From the API**

```bash
# Ask a question in Arabic using Aya model
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "ما هو الذكاء الاصطناعي؟",
    "model": "aya",
    "document_id": null
  }'
```

### **From the Frontend**

The system automatically detects the language of your question and responds in the same language. To use a specific model:

1. **Upload your Arabic document** (PDF, DOCX, TXT, etc.)
2. **Select the model** from the dropdown (choose "Aya" for best Arabic support)
3. **Ask your question in Arabic**
4. **Receive intelligent Arabic answers**

---

## 🎯 Model Selection Guide

| Use Case | Recommended Model | Why? |
|----------|------------------|------|
| Arabic documents & questions | **Aya** | Native Arabic support, professional writing |
| Mixed Arabic/English content | **Llama 3.2** | Good multilingual balance |
| English documents | **Llama 2** | Optimized for English |
| Fast responses (any language) | **Llama 3.2** | Smallest model, fastest inference |
| Maximum accuracy (Arabic) | **Aya** | Specialized multilingual model |

---

## 🔧 API Endpoints

### List Available Models
```bash
GET /api/models
```

**Response:**
```json
{
  "models": [
    {
      "name": "aya",
      "full_name": "aya:latest",
      "size": 5160000000,
      "description": "Multilingual model - Excellent for Arabic and 100+ languages"
    },
    {
      "name": "llama3.2",
      "full_name": "llama3.2:latest",
      "size": 2000000000,
      "description": "Latest Llama model - Better multilingual support"
    },
    {
      "name": "llama2",
      "full_name": "llama2:latest",
      "size": 3800000000,
      "description": "General purpose LLM - Good for English"
    }
  ],
  "default": "llama2"
}
```

### Chat with Model Selection
```bash
POST /api/chat
{
  "question": "سؤالك هنا",
  "model": "aya",
  "document_id": "optional-document-id",
  "stream": true
}
```

---

## 💡 Smart Language Detection

The system automatically:
- ✅ **Detects the language** of your question
- ✅ **Responds in the same language**
- ✅ **Maintains context** across multiple languages
- ✅ **Cites sources** in the original language

### Supported Languages (with Aya model):
- 🇸🇦 Arabic
- 🇬🇧 English
- 🇪🇸 Spanish
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇵🇹 Portuguese
- 🇷🇺 Russian
- 🇯🇵 Japanese
- 🇨🇳 Chinese
- 🇰🇷 Korean
- 🇮🇳 Hindi
- 🇹🇷 Turkish
- And 87+ more languages!

---

## 📝 Example Usage

### Arabic Question & Answer
**Question (Arabic):**
```
ما هي فوائد الذكاء الاصطناعي في التعليم؟
```

**Answer (Arabic - from Aya model):**
```
بناءً على المحتوى المقدم، فوائد الذكاء الاصطناعي في التعليم تشمل:
1. التعلم المخصص لكل طالب
2. التقييم الآلي والفوري
3. المساعدة في البحث والدراسة
[المصدر 1: education_ar.pdf]
```

### Mixed Language Support
You can upload documents in multiple languages and ask questions in any language - the system will maintain context and respond appropriately.

---

## ⚙️ Configuration

### Change Default Model

Edit `.env` file:
```bash
LLM_MODEL=aya  # For Arabic as default
# or
LLM_MODEL=llama3.2  # For multilingual
# or
LLM_MODEL=llama2  # For English (default)
```

Then restart backend:
```bash
docker compose restart backend
```

---

## 🎓 Best Practices

### For Arabic Documents:
1. **Use Aya model** for best results
2. **Upload Arabic documents** in PDF, DOCX, or TXT format
3. **Ask questions in Arabic** for native-language responses
4. **Be specific** in your questions for accurate citations

### For Performance:
1. **Use Llama 3.2** if you need faster responses
2. **Use smaller chunk sizes** for Arabic text (already optimized at 500 chars)
3. **Monitor GPU usage** with `nvidia-smi` during heavy Arabic processing

### For Accuracy:
1. **Always specify the model** explicitly when working with Arabic
2. **Review sources** to ensure context was properly understood
3. **Test with sample questions** before deploying to production

---

## 🔍 Troubleshooting

### Arabic Text Not Displaying Correctly
- Ensure your documents are UTF-8 encoded
- Use modern browsers with proper Arabic font support
- Check that PDF extraction preserved Arabic characters

### Model Not Found Error
- Run `docker exec ai-qa-ollama ollama list` to verify models
- Pull missing model: `docker exec ai-qa-ollama ollama pull aya`

### Slow Arabic Responses
- Arabic processing with Aya is GPU-intensive
- Monitor: `nvidia-smi` to check GPU utilization
- Consider using Llama 3.2 for faster (though less accurate) Arabic

---

## 📊 Performance Comparison

| Model | Arabic Quality | Speed | GPU Memory | Best Use |
|-------|---------------|-------|------------|----------|
| Aya | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 4.8 GB | Production Arabic |
| Llama 3.2 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2.0 GB | Fast multilingual |
| Llama 2 | ⭐⭐ | ⭐⭐⭐⭐ | 3.8 GB | English only |

---

## 🎉 Quick Test

Try this Arabic question to test the system:

```bash
curl -X POST https://8000-01kj0yn6syy1m1h2qsb8prdxpd.cloudspaces.litng.ai/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "اشرح لي ما هو نظام RAG",
    "model": "aya"
  }'
```

---

**Last Updated**: February 22, 2026  
**Models**: Aya (4.8GB), Llama 3.2 (2.0GB), Llama 2 (3.8GB)  
**Status**: ✅ All models loaded and ready with GPU acceleration
