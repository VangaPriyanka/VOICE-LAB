from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import whisper
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

# Load Whisper model
model = whisper.load_model("base")


@app.route('/')
def home():
    return render_template('index.html')


# ---------- TEXT TO SPEECH ----------
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():

    try:
        text = request.form.get('text')
        lang = request.form.get('lang')

        if not text or not lang:
            return jsonify({
                "error": "Missing text or language"
            }), 400

        # Translate text
        translated_text = GoogleTranslator(
            source='auto',
            target=lang
        ).translate(text)

        print("Translated:", translated_text)

        # Generate speech
        tts = gTTS(
            text=translated_text,
            lang=lang
        )

        output_file = "tts_output.mp3"

        tts.save(output_file)

        return send_file(
            output_file,
            mimetype="audio/mpeg"
        )

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# ---------- SPEECH TO TEXT ----------
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():

    try:

        file = request.files.get('audio')

        if not file:
            return jsonify({
                "error": "No file uploaded"
            }), 400

        filename = file.filename

        file_path = filename

        file.save(file_path)

        result = model.transcribe(file_path)

        return jsonify({
            "text": result["text"]
        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# ---------- SPEECH TO SPEECH ----------
# ---------- SPEECH TO SPEECH ----------
@app.route('/speech-to-speech', methods=['POST'])
def speech_to_speech():

    try:

        file = request.files.get('audio')
        target_lang = request.form.get('lang')

        if not file or not target_lang:
            return jsonify({
                "error": "Missing audio or language"
            }), 400

        # Save uploaded audio
        filename = file.filename

        input_path = filename

        file.save(input_path)

        # ---------- SPEECH TO TEXT ----------
        result = model.transcribe(input_path)

        text = result["text"].strip()

        # Whisper detected language
        detected_lang = result["language"]

        print("Detected Language:", detected_lang)
        print("Original Text:", text)
        print("Target Language:", target_lang)

        # ---------- TRANSLATION ----------
        translated_text = GoogleTranslator(
            source=detected_lang,
            target=target_lang
        ).translate(text)

        print("Translated Text:", translated_text)

        # ---------- TEXT TO SPEECH ----------
        tts = gTTS(
            text=translated_text,
            lang=target_lang
        )

        output_file = "speech_output.mp3"

        tts.save(output_file)

        # ---------- RETURN AUDIO ----------
        return send_file(
            output_file,
            mimetype="audio/mpeg"
        )

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)