FROM node:20-alpine

WORKDIR /app
RUN corepack enable

ENV NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000

CMD ["sh", "-lc", "pnpm install --frozen-lockfile && pnpm dev -- -H 0.0.0.0 -p 3000"]