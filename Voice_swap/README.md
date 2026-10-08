# Movie Scene Voice Swap

Upload a movie clip and a 20-30 second recording of your own voice. The notebook gives you the scene back with the dialogue in your voice, and the original music and effects kept in place.

## Files

| File | What it is |
|---|---|
| `voice_swap_colab.ipynb` | The notebook. Run it in Google Colab. |
| `requirements.txt` | Python packages the notebook needs, plus the system tools. |
| `README.md` | This file. |

## What you need

**Accounts and hardware**
- A Google account, to use Google Colab.
- A GPU runtime. The notebook is set up for a **T4 GPU** (`Runtime > Change runtime type > T4 GPU`).
- An internet connection. The first run downloads the models, and Colab prints a public `something.gradio.live` link for the app.

**Your inputs**
- A movie clip as a video file. Keep it short while you test, because every extra second adds processing time.
- Your voice: record 20-30 seconds in the app, or upload an mp3, wav, or m4a file. Only the first 30 seconds are used.

**Software** (all preinstalled or installed automatically on Colab)
- Python 3
- `ffmpeg` and `git`, both preinstalled on Colab
- Python packages listed in `requirements.txt`: `demucs`, `torchcodec`, `protobuf>=5.29,<7`
- Seed-VC, cloned from `https://github.com/Plachtaa/seed-vc` by Cell 1, together with its own requirements
- `torch`, `numpy`, and `gradio`, which Colab already provides (the notebook deliberately keeps Colab's versions)

## Run it on Colab

1. Upload `voice_swap_colab.ipynb` to Colab (`File > Upload notebook`).
2. Set `Runtime > Change runtime type > T4 GPU`, then `Save`.
3. Run **Cell 1**. It installs everything and takes a few minutes. Run it once per fresh runtime.
4. Run **Cell 2**. It patches Seed-VC, starts the app, and prints a `gradio.live` link.
5. Open the link, upload your clip, add your voice, and click **Convert**.
6. Download the result with the download icon on the video player. The app also gives you the converted dialogue as a separate audio file.

You can rerun Cell 2 any time without reinstalling, as long as the runtime has not been reset.

## What happens when you click Convert

1. `ffmpeg` pulls the audio out of your video and trims your voice sample to 30 seconds.
2. Demucs (`htdemucs`) splits the audio into dialogue and background (music and effects).
3. Seed-VC converts the dialogue to sound like your voice sample.
4. `ffmpeg` mixes your converted dialogue back over the original background and attaches it to the original video, which is copied without re-encoding.

## Settings in the app

- **Quality** (10-100, default 90): the number of diffusion steps. More steps give a closer match and take longer.
- **Voice strength** (0.3-1.0, default 0.95): higher is closer to your voice. Very high values can sound less smooth.

For the closest match, record somewhere quiet, speak continuously for the full 30 seconds, keep the mic steady and close, and use a natural pace.

## Run it locally (not tested)

The notebook is written for Colab: it uses `!` and `%cd` commands, `/content/...` paths, and `share=True`. To run it on your own machine you would need to adapt those parts. These are the requirements, which I have not tested:

- An NVIDIA GPU with a working CUDA setup.
- `ffmpeg` and `git` on your PATH.
- `torch` installed as the CUDA build from pytorch.org, plus `numpy` and `gradio`.
- `pip install -r requirements.txt`
- Seed-VC cloned and its own `requirements.txt` installed. Check the Seed-VC README for its supported Python version.
- The `/content/...` paths in Cell 2 changed to folders on your machine.

## Troubleshooting

- **Cell 1 or Cell 2 errors:** copy the full error text, not just the last line, when asking for help.
- **"The app did not receive an audio file":** upload a recording instead of using the mic button, or wait a couple of seconds after pressing stop before clicking Convert.
- **Version conflicts (protobuf, TensorFlow, huggingface_hub):** the notebook already includes fixes for these. If you see them again, the runtime may have been reset, so rerun Cell 1 first.
- **Slow first run:** the first conversion downloads models. Later runs in the same session are faster.

## Responsible use

Only use your own voice, or a voice you have permission to use, and only use clips you have the right to edit.
