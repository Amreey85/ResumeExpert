from flask import Flask, request, render_template, jsonify
import os
import PyPDF2
import docx
import re
from collections import Counter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Offline Analysis Core
class ResumeAnalyzer:
    def __init__(self):
        self.keyword_weights = {
            'skills': 1.2,
            'experience': 1.5,
            'education': 1.1
        }

    def extract_text(self, filepath):
        if filepath.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                return ''.join([p.extract_text() for p in PyPDF2.PdfReader(f).pages])
        elif filepath.endswith('.docx'):
            return '\n'.join([p.text for p in docx.Document(filepath).paragraphs])
        else:
            with open(filepath, 'r') as f:
                return f.read()

    def analyze(self, text, keywords):
        text = text.lower()
        matches = {kw: text.count(kw.lower()) for kw in keywords}
        total_score = sum(count * self.keyword_weights.get(kw, 1.0) for kw, count in matches.items())
        return {'matches': matches, 'score': min(total_score * 10, 100)}

# AI Integration (Online)
class AIIntegration:
    @staticmethod
    def deepseek_analysis(text, keywords):
        # Implement DeepSeek API call here
        return {"score": 85, "analysis": "AI analysis placeholder"}

    @staticmethod
    def chatgpt_analysis(text, keywords):
        # Implement ChatGPT API call here
        return {"score": 90, "analysis": "AI analysis placeholder"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('resumes')
    results = []
    
    for file in files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        text = ResumeAnalyzer().extract_text(filepath)
        results.append({'name': file.filename, 'text': text})
    
    return jsonify(results)

@app.route('/analyze', methods=['POST'])
def analyze_resumes():
    data = request.json
    analyzer = ResumeAnalyzer()
    ai_type = data.get('ai_type', 'offline')
    
    results = []
    for resume in data['resumes']:
        text = resume['text']
        
        if ai_type == 'deepseek':
            analysis = AIIntegration.deepseek_analysis(text, data['keywords'])
        elif ai_type == 'chatgpt':
            analysis = AIIntegration.chatgpt_analysis(text, data['keywords'])
        else:
            analysis = analyzer.analyze(text, data['keywords'])
        
        results.append({
            'name': resume['name'],
            'score': analysis['score'],
            'details': analysis.get('analysis', 'Offline analysis')
        })
    
    return jsonify(sorted(results, key=lambda x: x['score'], reverse=True))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)