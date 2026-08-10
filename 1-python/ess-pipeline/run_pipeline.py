# run_pipeline_demo.py


from source import source_and_accelerator
from target import target
from guide import neutron_guide
from sample import sample
from detector import detector


def main():

    # 1. Produce protons
    protons = source_and_accelerator()
    print(protons["message"])

    # 2. Produce neutrons
    neutrons = target(protons)
    print(neutrons["message"])

    # 3. Transport neutrons
    transported = neutron_guide(neutrons)
    print(transported["message"])

    # 4. Interact with sample
    after_sample = sample(transported)
    print(after_sample["message"])

    # 5. Detect them
    results = detector(after_sample)
    print(results["message"])

    # print("Number of protons:", len(protons["x"]))
    # print("Number of neutrons:", len(neutrons["x"]))
    # print("Detector image:", results["image"].shape)


if __name__ == "__main__":
    main()
