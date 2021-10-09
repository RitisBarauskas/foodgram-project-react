# build env
FROM node:14.17.6-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install --no-package-lock
COPY . ./
RUN npm install -g npm-install-peers
RUN npm-install-peers
RUN npm run build
CMD cp -r build result_build
