# base image
FROM node:16-alpine

# set working directory
WORKDIR /app/solution/ui/prototype

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/solution/ui/prototype/node_modules/.bin:$PATH

# install and cache app dependencies
COPY package.json /app/solution/ui/prototype/package.json
RUN npm install
RUN npm install @vue/cli@4.5.15 -g

# start app
CMD ["npm", "run", "serve"]
