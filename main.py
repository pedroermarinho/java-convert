import usecases_impl
import usecases

if __name__ == "__main__":
    # Uso do exemplo
    source_directory = "caminho_para_a_pasta_de_origem_service"

    usecases.create_use_cases(source_directory)
    usecases_impl.create_use_cases_impl(source_directory)

