{{- define "dev-envs.labels" -}}
app.kubernetes.io/name: dev-envs
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "dev-envs.selectorLabels" -}}
app: dev-envs-api
{{- end }}