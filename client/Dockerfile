FROM node:20 AS builder

WORKDIR /app
COPY client/package*.json ./
RUN npm install

COPY client/ ./

ARG VITE_SERVER_HOST_ADDRESS
ARG VITE_STATUS_THRESHOLD

ENV VITE_SERVER_HOST_ADDRESS=$VITE_SERVER_HOST_ADDRESS
ENV VITE_STATUS_THRESHOLD=$VITE_STATUS_THRESHOLD

RUN npm run build

FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]