import fetch from 'node-fetch';

const response = await fetch("https://8000-bekhruzrakhmono-idoctor-vzn6jybfk71.ws-eu34.gitpod.io/api/create-post/",{
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQ3NzA1NDQwLCJpYXQiOjE2NDcxMDQwMDAsImp0aSI6IjkzYzMzODk2ZDc1YzQ5ZGQ5NmE4NDE5Y2NlMDIzMDU0IiwidXNlcl9pZCI6ImFmY2Y0MmM2LWMwOTAtNDYxNS1hYTEzLTQyMmVmYmIzOTNiNCIsInVzZXIiOlsiYmVraHJ1enJha2htb25vdjJAZ21haWwuY29tIiwiRmVydXpiZWsgUmF4bW9ub3YiLCJteSBiaW8iXX0.JT_G3a5IFok87JW1AfMZKdkDe4vxWL6rv28QooiN-o4"
    },
    body: {
        "text": "Hello, it is my first post on iDoctor.",
        "photo": null
    }
})

const data = await response.status
console.log(data)