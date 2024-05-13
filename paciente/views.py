from django.shortcuts import render, HttpResponse
from medico.models import DadosMedico, Especialidades, DatasAbertas
from datetime import datetime

def home(request):
    if request.method == 'GET':
        medicos_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        print(especialidades_filtrar)
        medicos = DadosMedico.objects.all()
        if medicos_filtrar:
            medicos = medicos.filter(nome__icontains=medicos_filtrar)
        
        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

        especialidades = Especialidades.objects.all()
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades})

def escolher_horario(request, id_dados_medico):
    if request.method == 'GET':
        medico = DadosMedico.objects.get(id=id_dados_medico)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas})
    
def agendar_horario(request, id_data_aberta):
    if request.method == 'GET':
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        return HttpResponse(id_data_aberta)