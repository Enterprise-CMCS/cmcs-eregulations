FROM public.ecr.aws/lambda/provided:al2023 as build

# install compiler
RUN dnf install -y golang
RUN go env -w GOPROXY=direct

# build parser
COPY . .
WORKDIR fr-parser
RUN go mod download
RUN go build -tags lambda.norpc -o /main

# copy artifacts to a clean image
FROM public.ecr.aws/lambda/provided:al2023
COPY --from=build /main /main
ENTRYPOINT [ "/main" ]
