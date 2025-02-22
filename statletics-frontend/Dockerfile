# Utiliser une image de base alpine pour construire l'application
FROM node:23-alpine AS builder

# Définir le répertoire de travail
WORKDIR /app-frontend

# Copier package.json (et package-lock.json si présent) depuis statletics-frontend
COPY statletics-frontend/package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le reste des fichiers
COPY statletics-frontend/ ./

# Construire l'application avec npm run build
RUN npm run build

# Utiliser nginx pour servir l'application
FROM nginx:alpine

# Copier le build depuis /app-frontend/dist
COPY --from=builder /app-frontend/dist /usr/share/nginx/html

# Exposer le port 80
EXPOSE 80

# Démarrer nginx
CMD ["nginx", "-g", "daemon off;"]
