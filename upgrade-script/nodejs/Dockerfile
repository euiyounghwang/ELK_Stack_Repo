
# docker build -t my-nodejs-app .
# docker run -p 4000:3000 -d my-nodejs-app

FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]