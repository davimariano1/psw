from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from .models import Especialidades, DadosMedico, is_medico

def cadastro_medico(request):

    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Usuário já cadastrado como médico!")
        return redirect('/medicos/abrir_horario')

    if request.method == "GET":
        especialidade = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidade': especialidade})
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cedula_identidade_medico = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')
        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            rua=rua,
            bairro=bairro,
            numero=numero,
            cedula_identidade_medico=cedula_identidade_medico,
            rg=rg,
            foto=foto,
            especialidade_id=especialidade,
            descricao=descricao,
            valor_consulta=valor_consulta,
            user = request.user 
        )
        dados_medico.save()
        messages.add_message(request,constants.SUCCESS, "Cadastro realizado com sucesso!")
        return redirect('/usuarios/login')