import util
import generate_datasets
import first_exp, second_exp, third_exp

if __name__ == "__main__":
    ###############################################################
    #                         DATASETS                            #
    ###############################################################
    dataset, dataset_canarin_seconds, dataset_canarin_minutes =  generate_datasets.gen()
    ###############################################################
    #                           MODELS                            #
    ###############################################################
    first_exp.models(dataset)
    second_exp.models(dataset_canarin_seconds)
    third_exp.models(dataset_canarin_minutes)
