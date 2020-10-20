#!/bin/bash

set +x

if [ -n "$CTKEY_USERNAME" ]; then
  rm -rf ctkey ctkey.zip
  curl -O https://ctkey.s3.amazonaws.com/ctkey.zip
  unzip ctkey.zip -d ctkey
  mkdir ~/.aws
  ./ctkey/ctkey-linux savecreds --url=$CTKEY_URL --account=$CTKEY_ACCOUNT_ID --iam-role=$CTKEY_IAM_ROLE --idms=2
  echo "export AWS_PROFILE=${CTKEY_ACCOUNT_ID}_${CTKEY_IAM_ROLE}" >> $BASH_ENV
fi
