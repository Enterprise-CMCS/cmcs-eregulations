import { beforeAll, afterEach, afterAll } from "vitest";
import { setupServer } from "msw/node";
import handlers from "../../msw/mocks/handlers";
// import "whatwg-fetch";

const server = setupServer(...handlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));

afterAll(() => server.close());

afterEach(() => server.resetHandlers());
