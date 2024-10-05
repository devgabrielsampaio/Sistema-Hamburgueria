#69.856.244/0001-77
def validar_cpnj(cnpj):
    if len(cnpj) < 18:
        return False
    if len(cnpj)==18:
        try:
            n1 = int(cnpj[0])
            n2 = int(cnpj[1])
            n3 = int(cnpj[3])
            n4 = int(cnpj[4])
            n5 = int(cnpj[5])
            n6 = int(cnpj[7])
            n7 = int(cnpj[8])
            n8 = int(cnpj[9])
            n9 = int(cnpj[11])
            n10 = int(cnpj[12])
            n11 = int(cnpj[13])
            n12 = int(cnpj[14])
            digito1 = int(cnpj[16])
            digito2 = int(cnpj[17])
            if n1 == 0 and n2 == 0 and n3 == 0 and n4 == 0 and n5 == 0 and n6 == 0 and n7 == 0 and n8 == 0 and n9 == 0 and n10 == 0 and n11 == 0 and n12 == 0 and digito1 == 0 and digito2 == 0:
                return False
            Soma1 = n1 * 5 + n2 * 4 + n3 * 3 + n4 * 2 + n5 * 9 + n6 * 8 + n7 * 7 + n8 * 6 + n9 * 5 + n10 * 4 + n11 * 3 + n12 * 2
            digitoVerificador1 = Soma1 % 11
            if digitoVerificador1 < 2:
                digitoVerificador1 = 0
            else:
                digitoVerificador1 = 11 - digitoVerificador1
            Soma2 = n1 * 6 + n2 * 5 + n3 * 4 + n4 * 3 + n5 * 2 + n6 * 9 + n7 * 8 + n8 * 7 + n9 * 6 + n10 * 5 + n11 * 4 + n12 * 3 + digitoVerificador1 * 2
            digitoVerificador2 = Soma2 % 11
            if digitoVerificador2 < 2:
                digitoVerificador2 = 0
            else:
                digitoVerificador2 = 11 - digitoVerificador2
            if digito1 == digitoVerificador1 and digito2 == digitoVerificador2:
                return True
            else:
                return False
        except:
            return False
    else:
        return False