import pickle

if __name__ == "__main__":
    with open("occurances_output/225bd4c0-4b9f-4780-8ba0-82aa41ec2149", "rb") as f:
        print(pickle.load(f))
