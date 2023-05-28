import sys
import requests

headers = {'Authorization': 'Bearer ' + sys.argv[1]}

user_id = '31rrv4aepykcbnlkqqr74ywupds4'
track_ids = ['spotify:track:7w76bbcIF3nNBGbE741rcd', 'spotify:track:0XCgsvxtUHI5Dy0P0nAp4r',
             'spotify:track:76OGwb5RA9h4FxQPT33ekc', 'spotify:track:0gYXw7aPoybWFfB7btQ0eM',
             'spotify:track:6KhcA4elAfvxHzNaJwWp0T', 'spotify:track:4uUG5RXrOk84mYEfFvj3cK',
             'spotify:track:57BrnGF7ko9Vsrs8iDp0id', 'spotify:track:3nqQXoyQOWXiESFLlDF1hG',
             'spotify:track:5XeFesFbtLpXzIVDNQP22n']

server = 'https://api.spotify.com/v1'
response = requests.get(server + '/me', headers=headers)

playlists_path = '/users/' + response.json()['id'] + '/playlists'

playlists_to_delete = []
created_playlists = []

limit = {'limit': 50}
response = requests.get(server + playlists_path, headers=headers, params=limit)

response_json = response.json()

# Delete all playlists
for item in response_json['items']:
    print('Deleting playlist with id ' + item['id'])
    print(requests.delete(server + '/playlists/' + item['id'] + '/followers', headers=headers))

# Create 5 playlists
for x in range(5):
    name = 'Automatic playlist ' + str(x)
    response = requests.post(server + playlists_path, headers=headers,
                             data='{"name":"' + name + '","collaborative":false,"public":false}')
    response_json = response.json()
    created_playlists.append(response_json['id'])

print(created_playlists)

pl_count = 0
for pl in created_playlists:

    uris = ''

    for x in range(5):
        uris = uris + '"' + track_ids[x + pl_count] + '"'
        if x < 4:
            uris = uris + ','

    print(uris)

    print(requests.post(server + '/playlists/' + pl + '/tracks', headers=headers, data='{"uris":[' + uris + ']}'))

    pl_count = pl_count + 1