# In-cluster GitHub Actions -runner

## Miksi runner toteutettiin?

Runner tuo GitHub Actions -työt Kubernetes-klusterin sisälle. Näin workflow
pääsee käyttämään Kubeflow Pipelinesia klusterin sisäisellä osoitteella ilman,
että KFP tarvitsee avata julkiseen verkkoon tai paikallisen koneen kautta.

## Hyödyt paikalliseen runneriin verrattuna

- Työt suoritetaan klusterissa, eivät kehittäjän omalla koneella.
- Runner-podi voidaan käynnistää työtä varten ja poistaa sen jälkeen.
- Podin oikeuksia on rajattu: se toimii ei-root-käyttäjänä, ei saa ylimääräisiä
  Linux-kapabiliteetteja eikä Kubernetes-tokenia automaattisesti.
- Runneriin ei liitetä Docker socketia eikä käytetä Docker-in-Dockeria.
- GitHubiin otetaan yhteys ulospäin; GitHubista ei tarvitse avata yhteyttä
  klusteriin.

Nämä asetukset pienentävät runnerin oikeuksia ja vaikutusaluetta. Ne eivät
yksinään takaa tietoturvaa: myös tunnisteet, klusteri ja workflowt pitää suojata.

## Miten toteutus toimii?

```text
GitHub Actions → ARC käynnistää runner-podin Kubernetesissa
               → runner lähettää demopipelinen Kubeflow Pipelinesiin
```

Workflow käyttää `runs-on: arc-mlops` -asetusta ja KFP:n sisäistä osoitetta:

```text
http://ml-pipeline.kubeflow.svc.cluster.local:8888
```

Osoite toimii vain klusterissa, eikä ole selaimessa avattava käyttöliittymä.

Toteutukseen kuuluu ARC:n asennus- ja tarkistusskriptit, runnerin
suojausasetukset sekä workflow, joka lähettää wine-quality-demopipelinen ja
odottaa sen valmistumista. GitHub PAT välitetään Kubernetes Secretiin eikä
tallenneta `config.env`-tiedostoon.

## Voiko käyttää edelleen paikallista runneria?

Kyllä. Paikallinen runner on edelleen mahdollinen, jos sillä on yhteys KFP:hen
ja se käyttää saavutettavaa `KFP_ENDPOINT`-osoitetta. Nykyinen demo-workflow
on kuitenkin kohdistettu ARC-runneriin (`runs-on: arc-mlops`). Paikallisen
runnerin käyttö vaatii sille saman labelin tai workflow’n `runs-on`-asetuksen
vaihtamisen paikallisen runnerin labeliin. Paikallisessa kehityksessä KFP:n
oletusosoite on `http://localhost:8080`.

## Testitulos

GitHub Actions -ajo [#6](https://github.com/Softala-MLOPS/oss-mlops-platform/actions/runs/45401676520)
suoritti koko demopipelinen onnistuneesti.

