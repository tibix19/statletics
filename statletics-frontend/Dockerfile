# Utiliser une image de base alpine pour construire l'application
FROM node:23-alpine AS builder

# Définir le répertoire de travail
WORKDIR /app-frontend

# Copier package.json (et package-lock.json si présent) depuis statletics-frontend
COPY package*.json ./

# Installer les dépendances et mettre à jour les packages npm
RUN npm ci
RUN npm update

# Copier le reste des fichiers
COPY . .

# Construire l'application avec npm run build
RUN npm run build

# Utiliser nginx pour servir l'application
FROM nginx:alpine

# Copier le build depuis /app-frontend/dist
COPY --from=builder /app-frontend/dist /usr/share/nginx/html

# Copier le fichier de configuration nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposer le port 80
EXPOSE 80

# Démarrer nginx
CMD ["nginx", "-g", "daemon off;"]