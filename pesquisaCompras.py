import re
import pandas as pd
from scrapingCarrefour import carrefour
from scrapingHortiFruti import hortifruti
from scrapingPaodeAcucar import pao_de_acucar
from scrapingPrezunic import prezunic
from scrapingZonaSul import zona_sul

prod_cesta_basica = {"leguminosa":"arroz branco 1kg", "cereais":"feijão preto 1kg", "raizes":"batata", "legumes":"cebola", "frutas":"banana prata", "oleaginosas":"castanha caju", "carne":"ovos brancos", "leite":"leite pó integral 400", "oleos":"óleo de soja 900", "cafe":"café 500"}

def busca_valores(mercado):
    cesta_mercado = {}
    for grupo in prod_cesta_basica.keys():
        cesta_mercado[grupo] = mercado.recupera_produtos(mercado.busca_produto(prod_cesta_basica[grupo]))

    return cesta_mercado

def filtrar_cesta(cesta_mercado):
    cesta_filtrada = {}
    # loop para todos os grupos da cesta básica
    for grupo in cesta_mercado.keys():
        prod_cesta = prod_cesta_basica[grupo].split()
        # loop para cada produto recuperada pelo filtro do mercado
        for produto,preco in cesta_mercado[grupo].items():
            produto_selecionado = True
            # loop para um match do produto filtrado com o buscado, pois vem muitos produtos desnecessarios
            for part_prod_cesta in prod_cesta:
                pattern = re.compile(part_prod_cesta, re.IGNORECASE)
                if not re.search(pattern,produto):
                    produto_selecionado = False
                    break
            # se o produto tem todas as palavras do filtro
            if produto_selecionado:
                # tratamento do preco
                if preco != '' and preco != 'INDISPONIVEL':
                    preco = preco.replace("R$\xa0","")
                    preco = re.sub(r'[a-zA-Z/$]',"",preco)
                    preco = float(preco.replace(",","."))
                    preco = tratamento_medidas(produto,preco)
                    # ainda nao tem o produto para o grupo
                    if not grupo in cesta_filtrada:
                        cesta_filtrada[grupo]=(produto,preco)
                    # caso ja tenha, pegar o de menor preco
                    else:
                        # verificar a quantidade de nomes no titulo do produto, quanto mais proximo do padrão melhor
                        dif_label_prod = abs(len(prod_cesta)-len(cesta_filtrada[grupo][0].split()))
                        dif_label_prod_selecionado = abs(len(prod_cesta)-len(produto.split()))
                        if dif_label_prod > dif_label_prod_selecionado and preco < cesta_filtrada[grupo][1]:
                            cesta_filtrada[grupo]=(produto,preco)
    return cesta_filtrada

def tratamento_medidas(titulo_prod,preco):

    preco_final = preco
    re_kg = re.search('([0-9]+)\s*[kK][gG]',titulo_prod)
    re_g = re.search('([0-9]+)\s*[gG]',titulo_prod)
    re_unid = re.search('([0-9]+)\s*[Uu][nid]',titulo_prod)
    # medidas em kilos
    if re_kg:
        if int(re_kg.group(1)) > 1:
            preco_final = preco/int(re_kg.group(1))
    # medidas em gramas
    elif re_g:
        preco_final = (preco*1000)/int(re_g.group(1))
    # unidades no caso dos ovos sao 20 unidades a menor quantidade
    elif re_unid:
        if int(re_unid.group(1)) != 20:
            preco_final = (preco*20)/int(re_unid.group(1))
    # sem medida, considerar uma unidade pesando 150 g
    elif "Cebola" in titulo_prod or "Batata" in titulo_prod or "Banana" in titulo_prod:
        preco_final = (preco*1000)/150

    return preco_final

def insere_prods_mercado(nome_mercado,cesta_filtrada):

    #index_value = df_mercados.size
    #df_mercados.at[index_value,'mercado'] = nome_mercado
    mercado_dic = {}
    for grupo in cesta_filtrada.keys():
        if mercado_dic == {} or not grupo in mercado_dic.keys():
            mercado_dic[grupo] = [cesta_filtrada[grupo][1]]
        else:
            mercado_dic[grupo].append(cesta_filtrada[grupo][1])
    
    df = pd.DataFrame(mercado_dic, index=[nome_mercado])
    return df


if __name__ == "__main__":

    df_mercados = pd.DataFrame()
    '''
    ### Scraping Carrefour ###
    nome_mercado = "Carrefour"
    carrefour = carrefour()
    cesta_carrefour = busca_valores(carrefour)
    cesta_carrefour_filtrada = filtrar_cesta(cesta_carrefour)
    #cesta_carrefour_filtrada = {'leguminosa': ('Arroz Branco Longo-fino Tipo 1 Camil Todo Dia 1Kg', 6.89), 'cereais': ('Feijão Preto Tipo 1 Kicaldo 1Kg', 7.59), 'raizes': ('Batata Doce Roxa Carrefour Aprox. 600g', 2.93), 'legumes': ('Cebola Carrefour Aprox. 500g', 3.44), 'frutas': ('Banana Prata                Hortmix', 8.49), 'oleaginosas': ('Castanha de Caju Yoki 100g', 25.39), 'carne': ('Ovos Brancos Carrefour com 12 Unidades', 9.39), 'leite': ('Leite em Pó Integral Itambé 400g', 16.79), 'oleos': ('Óleo de Soja Soya 900ml', 5.89), 'cafe': ('Café em Pó Melitta 500g', 19.99)}
    df_mercados = pd.concat([df_mercados,insere_prods_mercado(nome_mercado, cesta_carrefour_filtrada)],axis=0)

    print(df_mercados)

    ### Scraping Hortifruti ###
    nome_mercado = "Hortifruti"
    horti = hortifruti()
    cesta_hortifruti = busca_valores(horti)
    cesta_hortifruti_filtrada = filtrar_cesta(cesta_hortifruti)
    #cesta_hortifruti_filtrada = {'leguminosa': ('Arroz Branco Longo-fino Tipo 1 Camil Todo Dia 1Kg', 6.89), 'cereais': ('Feijão Preto Tipo 1 Kicaldo 1Kg', 7.59), 'raizes': ('Batata Doce Roxa Carrefour Aprox. 600g', 2.93), 'legumes': ('Cebola Carrefour Aprox. 500g', 3.44), 'frutas': ('Banana Prata                Hortmix', 8.49), 'oleaginosas': ('Castanha de Caju Yoki 100g', 25.39), 'carne': ('Ovos Brancos Carrefour com 12 Unidades', 9.39), 'leite': ('Leite em Pó Integral Itambé 400g', 16.79), 'oleos': ('Óleo de Soja Soya 900ml', 5.89), 'cafe': ('Café em Pó Melitta 500g', 19.99)}
    df_mercados = pd.concat([df_mercados,insere_prods_mercado(nome_mercado, cesta_hortifruti_filtrada)],axis=0)
    
    print(df_mercados)
    
    ### Scraping Pao de Acucar ###
    nome_mercado = "Pao de Acucar"
    pao = pao_de_acucar()
    cesta_pao_de_acucar = busca_valores(pao)
    cesta_pao_de_acucar_filtrada = filtrar_cesta(cesta_pao_de_acucar)
    df_mercados = pd.concat([df_mercados,insere_prods_mercado(nome_mercado, cesta_pao_de_acucar_filtrada)],axis=0)
    
    print(df_mercados)
    '''
    ### Scraping Prezunic ###
    nome_mercado = "Prezunic"
    prezunic = prezunic()
    #cesta_prezunic = busca_valores(prezunic)
    cesta_prezunic = {'leguminosa': {'Arroz Branco Tio João Tipo1 1Kg': 'R$10,39', 'Arroz Branco Carreteiro Tipo1 1Kg': 'R$8,09', 'Arroz Branco Combrasil 1Kg': 'R$6,89', 'Arroz Branco Camil Tipo1 1Kg': 'R$8,49', 'Arroz Máximo Branco T1 1Kg': 'R$8,09', 'Arroz Branco Tio Mingote Tipo1 1Kg': 'R$7,29', 'Arroz Branco Prezunic Tipo1 1Kg': 'R$8,09'}, 'cereais': {'Feijão Preto Combrasil Tipo1 1Kg': 'R$9,79', 'Feijão Preto Carreteiro Tipo1 1Kg': 'R$9,19', 'Feijão Preto Super Máximo Tipo1 1Kg': 'R$10,39', 'Feijão Preto Caldo Carioca 1Kg': 'R$8,09', 'Feijão Preto Prezunic 1Kg': 'R$8,69', 'Feijão Preto Tio Mingote Tipo1 1Kg': 'R$8,09'}, 'raizes': {'Batata Inglesa': 'R$2,25', 'Batata Asterix': 'R$2,25', 'Batata Doce Prezunic 500g': 'R$5,79', 'Batata Baroa Prezunic 350g': 'R$14,99', 'Batata Doce Orgânica Rio de Una 600g': 'R$9,19', 'Batata Inglesa Orgânica Rio de Una 500g': 'R$10,99', 'Mini Batata Prezunic a Vácuo 500g': 'R$11,49', 'Batata Prezunic Cubinho Higienizado a Vácuo 400g': 'R$10,39'}, 'legumes': {'Cebola Branca': 'R$1,73', 'Cebola Roxa': 'R$2,26', 'Cebola Pirulit Sete Fratelli 1Kg': 'R$9,19', 'Alho e Cebola Picados Prezunic 200g': 'R$7,29', 'Cebola Prezunic Picada em Conserva Pote 200g': 'R$5,79', 'Cebola Picada Prezunic Pote 200g': 'R$9,19', 'Cebola Granulada BR Spices Essencial c/ Tampa Dosadora Vidro 30g': 'R$15,59', 'Cebola, Alho e Salsa Kitano 40g': 'R$10,99'}, 'frutas': {'Banana Prata': 'R$1,52', 'Banana Prata Benassi Orgânica 800g': 'INDISPONIVEL'}, 'oleaginosas': {'Castanha-de-Caju Yoki Torrada e Salgada Pacote 100g': 'R$22,99', 'Castanha de Caju Prezunic Torrada e Salgada 200g': 'R$25,29', 'Bebida à Base de Castanha-de-Caju e Aveia A Tal da Castanha Barista Profissional Caixa 1l': 'R$29,89', 'Bebida à Base de Castanha-de-Caju e Coco A Tal da Castanha Orgânica Caixa1l': 'R$29,89', 'Castanha de Caju': 'R$25,40', 'Castanha de Caju Amigos do Bem Salgada 50g': 'R$14,19', 'Bebida à Base de Castanha-de-Caju e Amendoim A Tal da Castanha Caixa 1l': 'R$29,89', 'Bebida à Base de Castanha-de-Caju A Tal da Castanha Orgânica Original Caixa 1l': 'R$29,89'}, 'carne': {'Ovos Brancos Grandes Prezunic c/ 20 Unid': 'R$16,09', 'Ovos Brancos Grandes Prezunic c/ 30 Unid': 'R$25,29', 'Ovos Brancos Grandes Mantiqueira Happy Eggs c/ 30 Unid': 'R$29,89', 'Ovos Brancos Grandes Prezunic Bandeja c/ 12 unid': 'R$10,19', 'Ovos Brancos Kerovos c/ 30 Unid': 'R$25,29', 'Ovos Brancos Médios Mantiqueira Galinha Pintadinha c/ 12 Unid': 'R$12,09'}, 'leite': {'Leite em Pó Itambé Integral Instantâneo Pacote 400g': 'R$18,39'}, 'oleos': {'Óleo de Soja Soya Pet 900ml': 'R$6,89', 'Óleo de Girassol Soya Pet 900ml': 'R$14,99', 'Óleo Composto de Soja e Oliva Maria Tradicional Pet 500ml': 'R$21,89', 'Óleo de Canola Salada Pet 900ml': 'R$17,89', 'Óleo de Milho Salada Pet 900ml': 'R$18,39', 'Óleo Composto Olinda 500ml': 'R$18,39', 'Óleo Restaurador Peroba Madeiras Escuras 200ml': 'R$25,29', 'Óleo de Girassol Salada Pet 900ml': 'R$18,99'}, 'cafe': {'Café em Pó Melitta Torrado e Moído Tradicional 500g': 'R$24,19', 'Café Pilão Almofada 500g': 'R$24,19', 'Café em Pó Pilão Puro a Vácuo 500g': 'R$24,19', 'Café em Pó Melitta Torrado e Moído Extraforte Caixa 500g': 'R$24,19', 'Café Melitta Tradicional Pouch 500g': 'R$24,19', 'Café em Pó Pimpinela Golden Almofada 500g': 'R$21,89', 'Café em Pó Pimpinela Torrado e Moído Extraforte Pacote 500g': 'R$19,59', 'Café em Pó 3 Corações Torrado e Moído Extraforte a Vácuo 500g': 'R$21,89'}}
    cesta_prezunic_filtrada = filtrar_cesta(cesta_prezunic)
    df_mercados = pd.concat([df_mercados,insere_prods_mercado(nome_mercado, cesta_prezunic_filtrada)],axis=0)
    
    print(df_mercados)
    '''
    ### Scraping Zona Sul ###
    nome_mercado = "Zona Sul"
    zs = zona_sul()
    cesta_zona_sul = busca_valores(zs)
    cesta_zona_sul_filtrada = filtrar_cesta(cesta_zona_sul)
    df_mercados = pd.concat([df_mercados,insere_prods_mercado(nome_mercado, cesta_zona_sul_filtrada)],axis=0)
    
    print(df_mercados)
    '''
