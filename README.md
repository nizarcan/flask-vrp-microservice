<h1 align="center">FLASK-VRP-MICROSERVICE</h3>

---

<p align="center"> A simple HTTP microservice built with Flask that solves VRPs using Google's OR-Tools.
    <br> 
</p>

## ⛏️ Running

The service can be run directly with

```
python app.py
```

or with a Docker container

```
docker-compose up
```

at the root directory.

<p align="center"> Then a JSON in a format described below can be POST-requested to http://localhost:5000 to get a solution in JSON.
    <br> 
</p>

## 🔧 Project Structure

```
flask-vrp-microservice
|--- app.py -> Main Script
|
|--- controllers
|    |--- solver -> Controller script that handles request
|
|--- data
|    |--- input_data_[number]_orders.json -> Randomly generated input files for testing
|
|--- errors -> Custom errors for appropriate response generation
|
|--- models
     |--- vrp -> The model that solves the problem and returns solution
```

## 📝 Valid Request Structure

```
{
    "vehicles": [
      {
        "id": 1,                    Vehicle ID
        "start_index": 0,           Starting idx of vehicle
        "capacity": [4]             Vehicle capacity
      },
      ...
    ],
    "jobs": [
      {
        "id": 1,                    Job ID
        "location_index": 3,        Location idx of job
        "delivery": [2],            Demand of the job
        "service": 327              Predetermined service time
      },
    ...
    ],
    "matrix": List[List[Int]]       nxn matrix that represents the time it takes to get from one location_index to another
}

```

## 📝 Response Structure

```
{
    "routes": {
        "1": {
            "delivery_duration": 6037,
            "jobs": [
                "10",
                "2",
                "9",
                "7",
                "5",
                "4",
                "1",
                "8"
            ]
        },
        "2": {
            "delivery_duration": 1431,
            "jobs": [
                "6",
                "3"
            ]
        }
    },
    "total_delivery_duration": 7468
}
```

## ⛏️ Built Using <a name = "built_using"></a>

- [Flask](https://github.com/pallets/flask)
- [OR-Tools](https://github.com/google/or-tools)

## ✍️ Author

- [@nizarcan](https://github.com/nizarcan)
