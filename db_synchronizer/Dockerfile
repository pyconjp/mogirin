# syntax=docker/dockerfile:1.3-labs
FROM ftnext/standalone-firefox-helium:92.0-3.8.12-3.0.8

COPY --chown=1200 \
  download_participants_csv.py \
  upload_to_spreadsheet.py \
  entrypoint.sh \
  requirements.lock \
  /work/

WORKDIR /work

USER root

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends git
python3 -m pip install --no-cache-dir -r requirements.lock
rm requirements.lock
chmod u+x entrypoint.sh
EOF

USER 1200

ENTRYPOINT [ "./entrypoint.sh" ]
