from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas, is_medico
from datetime import datetime, timedelta
from paciente.models import Consulta, Documento

def cadastro_medico(request):

    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Usuário já possui cadastro como profissional!")
        return redirect('/medico/abrir_horario')

    if request.method == "GET":
        especialidade = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidade': especialidade, 'is_medico': is_medico(request.user)})
    
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
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
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

def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Área exclusiva para médicos!")
        return redirect('/usuarios/sair')
    hoje = datetime.now().date()
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id'))
    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Apenas médicos podem abrir horários!")
        return redirect('usuarios/home')
    
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        print("redirecionando para consulta area médico - 7")
        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos})
    
    elif request.method == 'POST':
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')
        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, "Essa consulta está cancelada!")
            return redirect(f'medico/consulta_area_medico/{id_consulta}')
        
        elif consulta.status == 'F':
            messages.add_message(request, constants.WARNING, "Essa consulta foi finalizada!")
            return redirect(f'medico/consulta_area_medico/{id_consulta}')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()
        messages.add_message(request, constants.SUCCESS, "Consulta Iniciada!")
        return redirect(f'/medico/consulta_area_medico/{id_consulta}')
    
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.ERROR, "Apenas médicos podem finalizar consultas.")
        return redirect('/minhas_consultas')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, "Você não é o médico cadastrado para essa consulta!")
        return redirect('/usuarios/home')
    
    consulta.status = 'F'
    consulta.save()
    return redirect(f'/medico/consulta_area_medico/{id_consulta}')

def add_documento(request, id_consulta):
    print(request)
    if not is_medico(request.user):
        messages.add_message(request, constants.ERROR, "Você não pode inserir documentos para essa consulta!")
        return redirect('/usuarios/home')
    
    consulta = Consulta.objects.get(id=id_consulta)
    documentos = Documento.objects.filter(consulta=consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, "Você não é o médico cadastrado para essa consulta!")
        return redirect('/usuarios/home')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    if not documento:
        messages.add_message(request, constants.ERROR, "Preencha o campo documento")
        return redirect(f'/medico/consulta_area_medico/{id_consulta}')
    documento = Documento(
        consulta = consulta,
        titulo = titulo,
        documento = documento
    )
    
    documento.save()
    messages.add_message(request, constants.SUCCESS, "Documento salvo com sucesso!")
    return redirect(f'/medico/consulta_area_medico/{id_consulta}/')