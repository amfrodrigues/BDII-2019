import psycopg2
import datetime
from flask import Flask, render_template, url_for,request,redirect


app = Flask(__name__)
con = None
try:
    #conection to db
    con = psycopg2.connect(
        host="localhost",
        database="postgres",  # nome base dados
        user="postgres",
        password="root"  # pass acesso ao pgadmin
    )
    
    con.set_session(autocommit=True) #turn autocomit con

    # funçoes da app ----- inicio
    @app.route("/")
    def index():
        return render_template('index.html', title="Index")
        
    #-------------------------------- ementas -----------------------------
    @app.route("/ementas")
    def ementas():
        #iniciar cursor
        # todas as transacoes tens que ter cursores, aqui inicias a variavel
        db_ementas = con.cursor()
        #executar cursor
        # executas o cursor com o comando SQL
        #db_ementas.execute("select id_produto, id_ementa, produto, custo, tipoproduto,stock_produto, data, refeicao, nome_restaurante, tiporestaurante from produtos p join produtosementas z on  p.id_produto=z.idproduto_pe join ementas e on z.idementa_pe = e.id_ementa join datasementas d on e.iddata_ementa=d.id_data join locais l on l.id_local=e.idlocal_ementa and d.id_data=e.iddata_ementa join restaurantes r on l.idrestaurante_local=r.id_restaurante order by refeicao, tipoproduto")
        db_ementas.execute("select * from ViewEmentasRestaurante")
        #get data
        # fetchall é para ir buscar os dados todos da consulta, tambem do cursor (cursor é do psycopg2)
        array_db_ementa = db_ementas.fetchall()
        return render_template('vementas.html', title="Ementas", ementas=array_db_ementa)
    #-------------------------------- ementas -----------------------------
    @app.route("/pementa", methods=['GET', 'POST'])
    def pementa():
        id_func = request.form['func']
        id_cliente = request.form['client']
        id_prod = request.form['prod']
        id_local = request.form['local']
        qtd_prod = request.form['qtd']

        stringproc = id_func + "," + id_cliente + "," + id_prod + "," + id_local + "," + qtd_prod
        
        db_pementa = con.cursor()
        db_pementa.execute('call inserir_Vendas('+stringproc+') ')
        db_pementa.close()

        return redirect(url_for("ementas"))
    #--------------------------------repor stock -----------------------------
    #function to show qtd stock 
    @app.route("/stock",methods=['GET','POST'])
    def stock():
        db_stock = con.cursor()
        db_stock.execute("select * from produtos order by tipoproduto")
        array_db_stock = db_stock.fetchall()
        
        return render_template('stock.html', title='Stock', produtos=array_db_stock)

    #function to add qtd to stock and update price
    @app.route("/rstock", methods=['GET', 'POST'])
    def rstock():
        # data from form
        id = request.form['id_prod']
        qtd = request.form['nstock']
        pprod = request.form['precoprod']

        # call update procedure on db
        db_rstock = con.cursor()
        db_rstock.execute("call repor_stock(" + id + "," + qtd + "," + pprod + "::money)")
        db_rstock.close()
        return redirect(url_for('stock'))

    #-------------------------------- repor stock -----------------------------

    #-------------------------------- Vendas -----------------------------
    @app.route("/Vendas")
    def vendas():
        db_venda = con.cursor()
        db_venda.execute("select * from ViewPagarVendas")
        array_db_venda = db_venda.fetchall()
        db_venda.close()
        return render_template('vendas.html', title='VENDAS', vendas=array_db_venda)
    
    @app.route("/PVenda", methods=['GET', 'POST'])
    def pvenda():
        id = request.form['id_venda']
        db_pvenda = con.cursor()
        db_pvenda.execute("call pagar_venda(" + id + ")")
        db_venda.close()

        return redirect(url_for('vendas'))
    #-------------------------------- Vendas -----------------------------
    # funçoes da app ----- fim

    #-------------------------------- vendas funcionario -----------------------------
    @app.route("/vendasfunc")
    def vendasfunc():
        db_func = con.cursor()
        db_func.execute("select * from dadosfuncionarios")
        array_db_func = db_func.fetchall()
        db_func.close()
        return render_template('vendasfunc.html',title='VENDAS FUNCIONARIOS',funcionarios = array_db_func)

    #-------------------------------- Vendas funcionario -----------------------------
    #-------------------------------- Inserir -----------------------------
    @app.route("/adddados")
    def adddados():
        return render_template("adddados.html",title="Inserir na Database")
    
    @app.route("/addalergia", methods=['GET', 'POST'])
    def addalergia():
        nalergia = request.form['alergia']
        cur = con.cursor()
        cur.execute("call inserir_alergias(" + nalergia + ")")
        cur.close()

        return redirect(url_for('adddados'))
    
    @app.route("/add_tipo_ementa", methods=['GET', 'POST'])
    def add_tipo_ementa():
        tipo = request.form['tipo_ementa']
        cur = con.cursor()
        cur.execute("call inserir_TiposEmenta(" + tipo + ")")
        cur.close()
        return redirect(url_for('adddados'))

    @app.route("/add_cargo", methods=['GET', 'POST'])
    def add_cargo():
        cargo = request.form['cargo']
        cur = con.cursor()
        cur.execute("call inserir_Cargos(" + cargo + ")")
        cur.close()
        return redirect(url_for('adddados'))

    @app.route("/add_funcionario", methods=['GET', 'POST'])
    def add_funcionario():
        pnome = request.form['pnome']
        unome = request.form['unome']
        nident = request.form['nident']
        nib = request.form['nib']
        salario = request.form['salario']
        idcargo = request.form['idcargo']

        cur = con.cursor()
        cur.execute("call inserir_Funcionarios(" + pnome + ","+unome + ","+nident + ","+nib + ","+salario + "::money,"+idcargo+")")
        cur.close()

        return redirect(url_for('adddados'))

    @app.route("/add_produto", methods=['GET', 'POST'])
    def add_produto():
        nome = request.form['nome']
        custo = request.form['custo']
        tipo = request.form['tipo']
        alergia = request.form['alergia']
        stock = request.form['stock']

        cur = con.cursor()
        cur.execute("call inserir_Produtos(" + nome + ","+custo+"::money," + tipo+"," + alergia+"," +stock+ ")")
        cur.close()
        return redirect(url_for('adddados'))
    
    @app.route("/add_restaurante", methods=['GET', 'POST'])
    def add_restaurante():
        nome = request.form['nome']
        tipo = request.form['tipo']

        cur = con.cursor()
        cur.execute("call inserir_Restaurantes(" + nome + ","+ tipo +")")
        cur.close()

        return redirect(url_for('adddados'))

    @app.route("/add_local", methods=['GET', 'POST'])
    def add_local():
        morada = request.form['morada']
        codigo = request.form['codigo']
        abertura = request.form['abertura']
        fecho = request.form['fecho']
        telefone = request.form['telefone']
        correio = request.form['correio']
        rest = request.form['idrest']

        cur = con.cursor()
        cur.execute("call inserir_Locais(" + morada + "," + codigo + "," + abertura + ","+fecho + ","+telefone + ","+correio + ","+rest+")")
        cur.close()

        return redirect(url_for('adddados'))

    @app.route("/add_ementa", methods=['GET', 'POST'])
    def add_ementa():
        local = request.form['local']
        tipo = request.form['tipo']

        cur = con.cursor()
        cur.execute("call inserir_Ementas("+tipo + "," +local+ ")")
        cur.close()

        return redirect(url_for('adddados'))

    @app.route("/add_prodementa", methods=['GET', 'POST'])
    def add_prodementa():
        produto = request.form['produto']
        ementa = request.form['ementa']

        cur = con.cursor()
        cur.execute("call inserir_ProdutosEmentas("+produto + "," + ementa + ")")
        cur.close()

        return redirect(url_for('adddados'))

    @app.route("/add_locais_venda", methods=['GET', 'POST'])
    def add_locais_venda():
        local = request.form['local']
        nome = request.form['nome']

        cur = con.cursor()
        cur.execute("call inserir_LocaisVendas(" + local + "," + nome + ")")
        cur.close()

        return redirect(url_for('adddados'))

    @app.route("/add_cliente", methods=['GET', 'POST'])
    def add_cliente():
        pnome = request.form['pnome']
        unome = request.form['unome']
        nif = request.form['nif']
        cp = request.form['cp']

        cur = con.cursor()
        cur.execute("call inserir_Clientes(" + pnome + "," + unome + "," + nif + "," + cp + ")")
        cur.close()

        return redirect(url_for('adddados'))
    #-------------------------------- Inserir  -----------------------------

    #run the app 
    if __name__ == "__main__":
        app.run(debug=True)

except psycopg2.DatabaseError as error:
    con.rollback()
finally:
    if con is not None:
        con.close()
