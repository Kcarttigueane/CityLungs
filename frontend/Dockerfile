FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose the port
EXPOSE 3000

# For development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]