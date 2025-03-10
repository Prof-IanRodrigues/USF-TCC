from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    referencia_formatada = None
    
    if request.method == "POST":
        autor = request.form["autor"]
        titulo = request.form["titulo"]
        edicao = request.form["edicao"]
        ano = request.form["ano"]
        editora = request.form["editora"]
        local = request.form["local"]
        paginas = request.form["paginas"]
        
        # Gerando a referência no formato ABNT
        referencia_formatada = f"{autor.upper()}, {autor.split()[-1]}. <b>{titulo}</b>. {edicao}. {local}: {editora}, {ano}, p. {paginas}."

    return render_template("index.html", referencia=referencia_formatada)

if __name__ == "__main__":
    app.run(debug=True)
