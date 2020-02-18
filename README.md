### Installing
```
docker-compose build
docker-compose up -d
```
### Scrap images
```
POST http://127.0.0.1:5000/images/scrap/<URL>
```
### Get status of task for images
```
GET http://127.0.0.1:5000/images/status/<URL_or_ID>
```
### Download images
```
GET http://127.0.0.1:5000/images/download/<URL_or_ID>
```

### Scrap text
```
POST http://127.0.0.1:5000/text/scrap/<URL>
```
### Get status of task for text
```
GET http://127.0.0.1:5000/text/status/<URL_or_ID>
```
### Download text
```
GET http://127.0.0.1:5000/text/download/<URL_or_ID>
```