# Text-to-Speech Generator Module
"""
Text-to-Speech Generator Module

This module handles the generation of voiceovers for video ads using various
text-to-speech engines.
"""

import os
import logging
import time
import tempfile
from typing import Dict, Any, Optional, List

from .utils import setup_logger, clean_text_for_tts, generate_unique_filename

# Setup logger
logger = setup_logger('tts_generator')

def generate_voiceover(
    script: str,
    voice: str = "default",
    output_path: Optional[str] = None,
    engine: str = "openai",
    speed: float = 1.0,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a voiceover from script text.
    
    Args:
        script: Script text for voiceover
        voice: Voice style or ID
        output_path: Output file path (optional)
        engine: TTS engine to use (openai, google, azure, local)
        speed: Speed multiplier (0.5-2.0)
        api_key: API key for the TTS service
        
    Returns:
        Dictionary with voiceover metadata and path
    """
    # Clean text for TTS
    cleaned_script = clean_text_for_tts(script)
    
    # Generate default output path if not provided
    if not output_path:
        os.makedirs("output/audio", exist_ok=True)
        output_path = os.path.join("output/audio", generate_unique_filename("voiceover", ".mp3"))
    
    # Select engine
    if engine == "openai":
        return _generate_with_openai(cleaned_script, voice, output_path, speed, api_key)
    elif engine == "google":
        return _generate_with_google(cleaned_script, voice, output_path, speed, api_key)
    elif engine == "azure":
        return _generate_with_azure(cleaned_script, voice, output_path, speed, api_key)
    elif engine == "local":
        return _generate_with_local(cleaned_script, voice, output_path, speed)
    else:
        logger.error(f"Unknown TTS engine: {engine}")
        return {
            'success': False,
            'error': f"Unknown TTS engine: {engine}",
            'output_path': None
        }

def _generate_with_openai(
    script: str,
    voice: str,
    output_path: str,
    speed: float,
    api_key: Optional[str]
) -> Dict[str, Any]:
    """
    Generate voiceover using OpenAI's TTS API.
    
    Args:
        script: Script text
        voice: Voice ID
        output_path: Output path
        speed: Speed multiplier
        api_key: OpenAI API key
        
    Returns:
        Dictionary with metadata
    """
    if not api_key:
        return {
            'success': False,
            'error': "OpenAI API key not provided",
            'output_path': None
        }
    
    try:
        from openai import OpenAI
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Map voice name to OpenAI voice
        voice_map = {
            "default": "alloy",
            "male": "onyx",
            "female": "nova",
            "professional": "echo",
            "warm": "shimmer",
            "enthusiastic": "fable"
        }
        
        # Use mapped voice or default to the provided value
        openai_voice = voice_map.get(voice.lower(), voice) if voice else "alloy"
        
        logger.info(f"Generating voiceover with OpenAI TTS using voice '{openai_voice}'")
        
        # Generate speech with OpenAI
        response = client.audio.speech.create(
            model="tts-1",
            voice=openai_voice,
            input=script,
            speed=speed
        )
        
        # Save to file
        response.stream_to_file(output_path)
        
        logger.info(f"Voiceover saved to {output_path}")
        
        return {
            'success': True,
            'engine': 'openai',
            'voice': openai_voice,
            'duration': _get_audio_duration(output_path),
            'output_path': output_path
        }
        
    except ImportError:
        logger.error("OpenAI package not installed. Please install with: pip install openai")
        return {
            'success': False,
            'error': "OpenAI package not installed",
            'output_path': None
        }
        
    except Exception as e:
        logger.error(f"Error generating voiceover with OpenAI: {e}")
        return {
            'success': False,
            'error': str(e),
            'output_path': None
        }

def _generate_with_google(
    script: str,
    voice: str,
    output_path: str,
    speed: float,
    api_key: Optional[str]
) -> Dict[str, Any]:
    """
    Generate voiceover using Google's Text-to-Speech API.
    
    Args:
        script: Script text
        voice: Voice ID
        output_path: Output path
        speed: Speed multiplier
        api_key: Google API key
        
    Returns:
        Dictionary with metadata
    """
    try:
        # Try to import Google Cloud TTS
        from google.cloud import texttospeech
        
        # Check for API key
        if api_key:
            # Set environment variable for API key
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key
        elif "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            logger.error("Google Cloud credentials not provided")
            return {
                'success': False,
                'error': "Google Cloud credentials not provided",
                'output_path': None
            }
        
        # Initialize TTS client
        client = texttospeech.TextToSpeechClient()
        
        # Map voice name to Google voice
        voice_map = {
            "default": "en-US-Neural2-F",
            "male": "en-US-Neural2-D",
            "female": "en-US-Neural2-F",
            "professional": "en-US-Neural2-J",
            "warm": "en-US-Neural2-C",
            "enthusiastic": "en-US-Neural2-H"
        }
        
        # Use mapped voice or default to the provided value
        google_voice = voice_map.get(voice.lower(), voice) if voice else "en-US-Neural2-F"
        
        # Set voice parameters
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=google_voice
        )
        
        # Set audio config
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speed
        )
        
        # Build synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=script)
        
        logger.info(f"Generating voiceover with Google TTS using voice '{google_voice}'")
        
        # Generate speech
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )
        
        # Save to file
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        logger.info(f"Voiceover saved to {output_path}")
        
        return {
            'success': True,
            'engine': 'google',
            'voice': google_voice,
            'duration': _get_audio_duration(output_path),
            'output_path': output_path
        }
        
    except ImportError:
        logger.error("Google Cloud TTS package not installed. Please install with: pip install google-cloud-texttospeech")
        return {
            'success': False,
            'error': "Google Cloud TTS package not installed",
            'output_path': None
        }
        
    except Exception as e:
        logger.error(f"Error generating voiceover with Google TTS: {e}")
        return {
            'success': False,
            'error': str(e),
            'output_path': None
        }

def _generate_with_azure(
    script: str,
    voice: str,
    output_path: str,
    speed: float,
    api_key: Optional[str]
) -> Dict[str, Any]:
    """
    Generate voiceover using Azure's Text-to-Speech API.
    
    Args:
        script: Script text
        voice: Voice ID
        output_path: Output path
        speed: Speed multiplier
        api_key: Azure API key
        
    Returns:
        Dictionary with metadata
    """
    try:
        # Try to import Azure Cognitive Services
        import azure.cognitiveservices.speech as speechsdk
        
        # Check for API key and region
        if not api_key:
            logger.error("Azure Speech API key not provided")
            return {
                'success': False,
                'error': "Azure Speech API key not provided",
                'output_path': None
            }
        
        # Get Azure region from environment or default to East US
        region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
        
        # Create a speech config
        speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        
        # Map voice name to Azure voice
        voice_map = {
            "default": "en-US-JennyNeural",
            "male": "en-US-GuyNeural",
            "female": "en-US-JennyNeural",
            "professional": "en-US-AriaNeural",
            "warm": "en-US-JennyNeural",
            "enthusiastic": "en-US-AriaNeural"
        }
        
        # Use mapped voice or default to the provided value
        azure_voice = voice_map.get(voice.lower(), voice) if voice else "en-US-JennyNeural"
        
        # Set voice
        speech_config.speech_synthesis_voice_name = azure_voice
        
        # Create an audio config for saving to file
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # Create a speech synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        # Create SSML to control speech characteristics
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{azure_voice}">
                <prosody rate="{speed*100-100:+.0f}%">
                    {script}
                </prosody>
            </voice>
        </speak>
        """
        
        logger.info(f"Generating voiceover with Azure TTS using voice '{azure_voice}'")
        
        # Generate speech
        result = synthesizer.speak_ssml_async(ssml).get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Voiceover saved to {output_path}")
            
            return {
                'success': True,
                'engine': 'azure',
                'voice': azure_voice,
                'duration': _get_audio_duration(output_path),
                'output_path': output_path
            }
        else:
            error = f"Speech synthesis failed: {result.reason}"
            logger.error(error)
            return {
                'success': False,
                'error': error,
                'output_path': None
            }
        
    except ImportError:
        logger.error("Azure Speech SDK not installed. Please install with: pip install azure-cognitiveservices-speech")
        return {
            'success': False,
            'error': "Azure Speech SDK not installed",
            'output_path': None
        }
        
    except Exception as e:
        logger.error(f"Error generating voiceover with Azure TTS: {e}")
        return {
            'success': False,
            'error': str(e),
            'output_path': None
        }

def _generate_with_local(
    script: str,
    voice: str,
    output_path: str,
    speed: float
) -> Dict[str, Any]:
    """
    Generate voiceover using a local TTS engine (pyttsx3).
    
    Args:
        script: Script text
        voice: Voice ID
        output_path: Output path
        speed: Speed multiplier
        
    Returns:
        Dictionary with metadata
    """
    try:
        # Try to import pyttsx3
        import pyttsx3
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty('rate', int(engine.getProperty('rate') * speed))
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        # Map voice name to index
        voice_map = {
            "default": 0,
            "male": 0,  # Usually the first voice is male
            "female": 1 if len(voices) > 1 else 0
        }
        
        # Set voice
        voice_idx = voice_map.get(voice.lower(), 0) if voice.lower() in voice_map else 0
        if voice_idx < len(voices):
            engine.setProperty('voice', voices[voice_idx].id)
        
        logger.info(f"Generating voiceover with local TTS using voice index {voice_idx}")
        
        # Save to file
        engine.save_to_file(script, output_path)
        engine.runAndWait()
        
        logger.info(f"Voiceover saved to {output_path}")
        
        return {
            'success': True,
            'engine': 'local',
            'voice': f"voice_{voice_idx}",
            'duration': _get_audio_duration(output_path),
            'output_path': output_path
        }
        
    except ImportError:
        logger.error("pyttsx3 not installed. Please install with: pip install pyttsx3")
        return {
            'success': False,
            'error': "pyttsx3 not installed",
            'output_path': None
        }
        
    except Exception as e:
        logger.error(f"Error generating voiceover with local TTS: {e}")
        return {
            'success': False,
            'error': str(e),
            'output_path': None
        }

def _get_audio_duration(file_path: str) -> float:
    """
    Get the duration of an audio file in seconds.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds or 0 if error
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        return audio.duration_seconds
    except ImportError:
        logger.warning("pydub not installed. Cannot determine audio duration.")
        return 0
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0

def adjust_audio_timing(
    audio_path: str,
    target_duration: float,
    output_path: Optional[str] = None,
    method: str = "speed"
) -> Dict[str, Any]:
    """
    Adjust audio timing to match target duration.
    
    Args:
        audio_path: Path to audio file
        target_duration: Target duration in seconds
        output_path: Output path (optional)
        method: Adjustment method ('speed', 'silence', 'stretch')
        
    Returns:
        Dictionary with adjusted audio metadata
    """
    try:
        from pydub import AudioSegment
        
        # Create default output path if not provided
        if not output_path:
            filename, ext = os.path.splitext(audio_path)
            output_path = f"{filename}_adjusted{ext}"
        
        # Load audio
        audio = AudioSegment.from_file(audio_path)
        current_duration = audio.duration_seconds
        
        # Skip if already the right duration
        if abs(current_duration - target_duration) < 0.1:
            return {
                'success': True,
                'method': 'none',
                'original_duration': current_duration,
                'adjusted_duration': current_duration,
                'output_path': audio_path
            }
        
        logger.info(f"Adjusting audio from {current_duration:.2f}s to {target_duration:.2f}s using {method}")
        
        # Adjust based on method
        if method == "speed":
            # Change playback speed
            speed_factor = current_duration / target_duration
            
            # Use FFmpeg for speed adjustment
            import subprocess
            import tempfile
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Call FFmpeg to adjust speed
            subprocess.run([
                "ffmpeg", "-y", "-i", audio_path, "-filter:a", 
                f"atempo={speed_factor}", output_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Verify duration
            adjusted_audio = AudioSegment.from_file(output_path)
            adjusted_duration = adjusted_audio.duration_seconds
            
        elif method == "silence":
            # Add silence to match target duration
            if current_duration < target_duration:
                # Need to add silence
                silence_duration = int((target_duration - current_duration) * 1000)
                silence = AudioSegment.silent(duration=silence_duration)
                
                # Add silence at the end
                adjusted_audio = audio + silence
            else:
                # Need to trim
                adjusted_audio = audio[:int(target_duration * 1000)]
            
            # Save
            adjusted_audio.export(output_path, format="mp3")
            adjusted_duration = adjusted_audio.duration_seconds
            
        elif method == "stretch":
            # Time stretch audio using librosa
            try:
                import librosa
                import soundfile as sf
                import numpy as np
                
                # Load audio using librosa
                y, sr = librosa.load(audio_path, sr=None)
                
                # Calculate stretch factor
                stretch_factor = target_duration / current_duration
                
                # Time stretch
                y_stretched = librosa.effects.time_stretch(y, rate=stretch_factor)
                
                # Save
                sf.write(output_path, y_stretched, sr)
                
                # Verify duration
                adjusted_audio = AudioSegment.from_file(output_path)
                adjusted_duration = adjusted_audio.duration_seconds
                
            except ImportError:
                logger.error("librosa and soundfile required for stretch method. Falling back to speed method.")
                return adjust_audio_timing(audio_path, target_duration, output_path, "speed")
        
        else:
            logger.error(f"Unknown timing adjustment method: {method}")
            return {
                'success': False,
                'error': f"Unknown method: {method}",
                'output_path': audio_path
            }
        
        logger.info(f"Adjusted audio saved to {output_path} (duration: {adjusted_duration:.2f}s)")
        
        return {
            'success': True,
            'method': method,
            'original_duration': current_duration,
            'adjusted_duration': adjusted_duration,
            'output_path': output_path
        }
        
    except ImportError as e:
        logger.error(f"Missing dependency for audio adjustment: {e}")
        return {
            'success': False,
            'error': f"Missing dependency: {str(e)}",
            'output_path': audio_path
        }
        
    except Exception as e:
        logger.error(f"Error adjusting audio timing: {e}")
        return {
            'success': False,
            'error': str(e),
            'output_path': audio_path
        }

if __name__ == "__main__":
    # Test the TTS generator
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    test_script = "Welcome to our premium video ad generator. This system creates high-converting advertisements for your brand."
    
    # Get API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openai_api_key:
        # Test OpenAI TTS
        result = generate_voiceover(
            script=test_script,
            voice="enthusiastic",
            engine="openai",
            api_key=openai_api_key
        )
        
        if result['success']:
            print(f"OpenAI TTS test successful: {result['output_path']}")
            print(f"Duration: {result['duration']:.2f}s")
            
            # Test timing adjustment
            timing_result = adjust_audio_timing(
                result['output_path'],
                8.0,  # Target 8 seconds
                method="speed"
            )
            
            if timing_result['success']:
                print(f"Timing adjustment successful:")
                print(f"Original duration: {timing_result['original_duration']:.2f}s")
                print(f"Adjusted duration: {timing_result['adjusted_duration']:.2f}s")
                print(f"Output: {timing_result['output_path']}")
            else:
                print(f"Timing adjustment failed: {timing_result.get('error', 'Unknown error')}")
        else:
            print(f"OpenAI TTS test failed: {result.get('error', 'Unknown error')}")
    else:
        # Test local TTS as fallback
        result = generate_voiceover(
            script=test_script,
            voice="default",
            engine="local"
        )
        
        if result['success']:
            print(f"Local TTS test successful: {result['output_path']}")
        else:
            print(f"Local TTS test failed: {result.get('error', 'Unknown error')}")
            
            # Simulate success for demo
            print("Creating a placeholder audio file for demonstration...")
            
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            # Create a simple tone
            sine = Sine(440)  # 440 Hz
            audio = sine.to_audio_segment(duration=5000)  # 5 seconds
            
            # Save to file
            os.makedirs("output/audio", exist_ok=True)
            output_path = "output/audio/placeholder.mp3"
            audio.export(output_path, format="mp3")
            
            print(f"Placeholder audio saved to {output_path}")