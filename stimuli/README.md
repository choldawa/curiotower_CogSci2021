### Stimulus preprocessing

#### Our pipeline for pilot0

1. Obtained directory of JPEG images from [curiobaby_drop](https://github.com/langcog/curiobaby_drop)
2. Converted JPEG to PNG: `jpg2png.py`
3. Uploaded PNGs to Amazon S3 so they have permanent URLs: `upload_stims_to_s3.py` (currently using cogtoolslab credentials) 
4. Create `metadata.js` that contains trial metadata for survey, including image URL and any other properties of interest




