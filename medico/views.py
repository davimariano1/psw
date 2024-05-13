from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from datetime import datetime


def cadastro_medico(request):

    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Usuário já possui cadastro como profissional!")
        return redirect('/medico/abrir_horario')

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
        return redirect('/medico/abrir_horario')

def abrir_horario(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Área exclusiva para médicos!")
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas})
    
    elif request.method == 'POST':
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        if data_formatada <= datetime.now():
            messages.add_message(request,constants.WARNING, "A data não pode ser anterior a data atual!!")
            return redirect('/medico/abrir_horario')
        print(data)
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )
        horario_abrir.save()
        messages.add_message(request, constants.SUCCESS, "Horário cadastrado com sucesso!!")
        return redirect('/medico/abrir_horario')