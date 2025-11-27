from locust import HttpUser, task, between


class FlaskUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def listar_productos(self):
        self.client.get("/productos")

    @task
    def home(self):
        self.client.get("/")
