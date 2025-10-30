from .pipeline import ModelManager

if __name__ == "__main__":
    mm = ModelManager()
    name, metrics = mm.train_and_save()
    print("Best model:", name)
    print("Metrics:", metrics)
