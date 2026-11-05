---
title: "VBAからREST APIを呼び出す共通関数"
description: "baseUrlとendpointを分離し、HTTPメソッド・プロキシ・クエリパラメータを切り替えるVBA実装。"
order: 7
category: "プログラミング / VBA"
tags: [program]
updated_at: "2026-11-05"
status: "実装例・動作未検証"
---

## 目的

VBAからREST APIを呼び出す共通関数を作る。**baseUrl**（APIのベースURL）と**endpoint**（相対パス）は別々の引数として渡し、内部で結合する。

- **HTTPメソッド**：GET / POST / PUT / DELETE
- **接続**：直接接続、または指定プロキシを経由
- **クエリ**：省略可。指定された値はUTF-8でURLエンコード
- **本文**：省略可。指定した文字列をUTF-8で送信
- **戻り値**：HTTPステータス・レスポンス本文・レスポンスヘッダー・成功フラグ・通信エラー

Windows版VBAを想定し、`WinHttp.WinHttpRequest.5.1`、`ADODB.Stream`、`Scripting.Dictionary` を遅延バインディングで利用する。標準モジュールへ貼り付ける想定で、参照設定の追加は不要。

## 実装コード

```vb
Option Explicit

Public Type ApiResponse
    StatusCode As Long
    Body As String
    Headers As String
    Succeeded As Boolean
    ErrorMessage As String
End Type

Public Function SendApiRequest( _
    ByVal method As String, _
    ByVal baseUrl As String, _
    ByVal endpoint As String, _
    Optional ByVal queryParams As Object = Nothing, _
    Optional ByVal requestBody As String = "", _
    Optional ByVal useProxy As Boolean = False, _
    Optional ByVal proxyAddress As String = "", _
    Optional ByVal contentType As String = "application/json; charset=utf-8", _
    Optional ByVal authorization As String = "" _
) As ApiResponse
    Dim result As ApiResponse
    Dim http As Object
    Dim url As String

    On Error GoTo RequestError

    method = UCase$(Trim$(method))
    Select Case method
        Case "GET", "POST", "PUT", "DELETE"
        Case Else
            Err.Raise vbObjectError + 1000, , "Unsupported HTTP method: " & method
    End Select

    url = JoinUrl(baseUrl, endpoint)
    If Not queryParams Is Nothing Then
        url = AppendQuery(url, queryParams)
    End If

    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")

    ' 1 = DIRECT, 2 = PROXY（Windowsの自動設定に依存させない）
    If useProxy Then
        If Len(Trim$(proxyAddress)) = 0 Then
            Err.Raise vbObjectError + 1001, , "Proxy address is required."
        End If
        http.SetProxy 2, proxyAddress
    Else
        http.SetProxy 1
    End If

    http.SetTimeouts 5000, 5000, 15000, 30000
    http.Open method, url, False
    http.SetRequestHeader "Accept", "application/json"

    If Len(authorization) > 0 Then
        http.SetRequestHeader "Authorization", authorization
    End If

    If Len(requestBody) > 0 Then
        http.SetRequestHeader "Content-Type", contentType
        http.Send Utf8Bytes(requestBody)
    Else
        http.Send
    End If

    result.StatusCode = http.Status
    result.Body = http.ResponseText
    result.Headers = http.GetAllResponseHeaders
    result.Succeeded = (result.StatusCode >= 200 And result.StatusCode < 300)

    SendApiRequest = result
    Exit Function

RequestError:
    result.Succeeded = False
    result.ErrorMessage = "VBA error " & Err.Number & ": " & Err.Description
    SendApiRequest = result
End Function

Private Function JoinUrl(ByVal baseUrl As String, ByVal endpoint As String) As String
    baseUrl = Trim$(baseUrl)
    endpoint = Trim$(endpoint)

    If LCase$(Left$(baseUrl, 8)) <> "https://" And _
       LCase$(Left$(baseUrl, 7)) <> "http://" Then
        Err.Raise vbObjectError + 1002, , "baseUrl must start with http:// or https://"
    End If

    If InStr(1, endpoint, "://", vbTextCompare) > 0 Then
        Err.Raise vbObjectError + 1003, , "endpoint must be a relative path."
    End If

    If InStr(baseUrl, "?") > 0 Or InStr(baseUrl, "#") > 0 Or _
       InStr(endpoint, "#") > 0 Then
        Err.Raise vbObjectError + 1004, , "Fragments and baseUrl queries are not supported."
    End If

    Do While Right$(baseUrl, 1) = "/"
        baseUrl = Left$(baseUrl, Len(baseUrl) - 1)
    Loop
    Do While Left$(endpoint, 1) = "/"
        endpoint = Mid$(endpoint, 2)
    Loop

    If Len(endpoint) = 0 Then
        JoinUrl = baseUrl
    Else
        JoinUrl = baseUrl & "/" & endpoint
    End If
End Function

Private Function AppendQuery(ByVal url As String, ByVal params As Object) As String
    Dim key As Variant
    Dim separator As String

    separator = IIf(InStr(url, "?") > 0, "&", "?")
    For Each key In params.Keys
        If IsNull(params(key)) Or IsEmpty(params(key)) Then
            Err.Raise vbObjectError + 1005, , "Query values cannot be Null or Empty."
        End If

        url = url & separator & UrlEncodeUtf8(CStr(key)) & "=" & _
              UrlEncodeUtf8(CStr(params(key)))
        separator = "&"
    Next key
    AppendQuery = url
End Function

Private Function UrlEncodeUtf8(ByVal value As String) As String
    Dim bytes As Variant
    Dim i As Long
    Dim n As Long
    Dim encoded As String

    If Len(value) = 0 Then Exit Function
    bytes = Utf8Bytes(value)

    For i = LBound(bytes) To UBound(bytes)
        n = CLng(bytes(i))
        If (n >= 65 And n <= 90) Or (n >= 97 And n <= 122) Or _
           (n >= 48 And n <= 57) Or n = 45 Or n = 46 Or _
           n = 95 Or n = 126 Then
            encoded = encoded & Chr$(n)
        Else
            encoded = encoded & "%" & Right$("0" & Hex$(n), 2)
        End If
    Next i

    UrlEncodeUtf8 = encoded
End Function

Private Function Utf8Bytes(ByVal value As String) As Variant
    Dim stream As Object

    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 2                  ' adTypeText
    stream.Charset = "utf-8"
    stream.Open
    stream.WriteText value
    stream.Position = 0
    stream.Type = 1                  ' adTypeBinary
    stream.Position = 3              ' ADODB.StreamのUTF-8 BOMを除去
    Utf8Bytes = stream.Read
    stream.Close
End Function

```

## GET：クエリパラメータを指定して取得する

APIの一覧取得を想定した例。認証が必要なAPIを想定して、アクセストークンを環境変数 `API_ACCESS_TOKEN` から取得する（認証不要のAPIなら、トークンのチェックと `authorization` 引数は省略できる）。

```vb
Public Sub ExampleGetBestPractice()
    Const BASE_URL As String = "https://api.example.com/v1"
    Dim token As String
    Dim params As Object
    Dim response As ApiResponse

    ' 例：APIがBearer認証を必要とする場合
    token = Environ$("API_ACCESS_TOKEN")
    If Len(Trim$(token)) = 0 Then
        Debug.Print "API_ACCESS_TOKEN が未設定です。"
        Exit Sub
    End If

    Set params = CreateObject("Scripting.Dictionary")
    params.Add "keyword", "日本語"
    params.Add "page", "1"

    response = SendApiRequest( _
        method:="GET", _
        baseUrl:=BASE_URL, _
        endpoint:="/items", _
        queryParams:=params, _
        authorization:="Bearer " & token _
    )

    ' 接続失敗（タイムアウト、DNS、プロキシなど）
    If Len(response.ErrorMessage) > 0 Then
        Debug.Print "GETの通信エラー: " & response.ErrorMessage
        Exit Sub
    End If

    ' HTTP 4xx / 5xx は通信できても正常応答ではない
    If Not response.Succeeded Then
        Debug.Print "GETのHTTPエラー: " & response.StatusCode
        Exit Sub
    End If

    Debug.Print "GET成功: HTTP " & response.StatusCode
    ' 必要に応じて response.Body をJSONとして解析して使う
    ' 実運用でレスポンス本文（個人情報等）を丸ごとログに出さない
End Sub
```

この例のリクエストURLは次のようになる。`baseUrl` と `endpoint` は別の値として管理し、クエリの値は共通関数側でエンコードする。

```text
https://api.example.com/v1/items?keyword=%E6%97%A5%E6%9C%AC%E8%AA%9E&page=1
```

**GETのポイント**：本文は送信せず、絞り込み条件などは `queryParams` で渡す。通信エラーとHTTPエラーを分けて扱い、成功時は `response.Body` をAPI仕様に従って解析する。個人情報や機密情報はクエリ文字列に載せない。

## POST：JSONを送信して新規作成する

新規データの作成を想定した例。`requestBody` にJSON文字列を渡すと、共通関数がUTF-8のバイト列で送信する。

```vb
Public Sub ExamplePostBestPractice()
    Const BASE_URL As String = "https://api.example.com/v1"
    Dim token As String
    Dim jsonBody As String
    Dim response As ApiResponse

    token = Environ$("API_ACCESS_TOKEN")
    If Len(Trim$(token)) = 0 Then
        Debug.Print "API_ACCESS_TOKEN が未設定です。"
        Exit Sub
    End If

    ' API仕様に合わせたJSONの固定例。
    ' 可変の文字列を埋め込む場合はJSONライブラリでシリアライズする
    jsonBody = "{""name"":""テスト"",""enabled"":true}"

    response = SendApiRequest( _
        method:="POST", _
        baseUrl:=BASE_URL, _
        endpoint:="/items", _
        requestBody:=jsonBody, _
        contentType:="application/json; charset=utf-8", _
        authorization:="Bearer " & token _
    )

    If Len(response.ErrorMessage) > 0 Then
        Debug.Print "POSTの通信エラー: " & response.ErrorMessage
        Exit Sub
    End If

    If Not response.Succeeded Then
        Debug.Print "POSTのHTTPエラー: " & response.StatusCode
        Exit Sub
    End If

    ' APIによって201 Created、200 OK、204 No Contentなどがあり得る
    Debug.Print "POST成功: HTTP " & response.StatusCode
    ' 返却ID等は必要に応じて response.Body からJSON解析する
End Sub
```

**POSTのポイント**：`Content-Type` と本文の形式を一致させる。例は固定JSONなのでそのまま書けるが、ユーザー入力などを埋め込む場合は、文字列連結ではなくJSONシリアライザーを使う。ステータスはAPIによって異なるため、`201` だけを成功条件にしない。また、タイムアウト時にはサーバーで処理済みの可能性があるので、**POSTを無条件に再試行しない**（必要ならAPIが提供する冪等キーなどの仕組みを確認する）。

### プロキシを経由する場合

GETとPOSTのどちらも、`SendApiRequest` 呼び出しに次の引数を追加する。環境変数 `API_PROXY` には、たとえば `proxy.example.com:8080` のような接続先を設定する。値が空の場合はプロキシ設定エラーになる。プロキシが不要な場合は両引数を省略し、明示的に直接接続する。

```vb
' 上記のSendApiRequest呼び出しに、必要なら追加する引数
useProxy:=True, _
proxyAddress:=Environ$("API_PROXY"), _
```

### PUT / DELETE の最小例

同じ共通関数でHTTPメソッドを切り替えられる。以下は**プロシージャ内に記述する処理の抜粋**で、実運用ではGET・POSTの例と同様に戻り値を判定する。

```vb
Dim response As ApiResponse

response = SendApiRequest( _
    method:="DELETE", _
    baseUrl:="https://api.example.com/v1", _
    endpoint:="/items/123" _
)

response = SendApiRequest( _
    method:="PUT", _
    baseUrl:="https://api.example.com/v1", _
    endpoint:="/items/123", _
    requestBody:="{""name"":""更新後""}" _
)
```

### サンプルを使う前に

- `api.example.com` は説明用のURLであり、実在するAPIのエンドポイントに置き換える。
- `API_ACCESS_TOKEN` はExcelを起動する前に利用環境で設定する。APIキーをVBAコードやリポジトリに直接記載しない。
- GETとPOSTの例は**前節の共通関数と同じ標準モジュールに追加**して利用する。認証方式・レスポンス形式・POST本文は接続先APIの仕様に従う。
- ここでは `Debug.Print` でHTTPステータスのみ出力する。実運用では本文・トークン・個人情報を不用意にログへ出力しない。

## 実装の注意

- `Succeeded` はHTTPステータス200～299で判定する。HTTP 4xx/5xxは通信成功でも `Succeeded=False` とし、`StatusCode` と `Body` に内容を残す。接続例外時には `ErrorMessage` を設定する。
- `Authorization` は必要な場合にだけ呼び出し側から渡す。アクセストークンをGitHubにコミットしない。
- `queryParams` には `Scripting.Dictionary` を渡す想定。同一キーの複数指定や配列値は未対応。
- `baseUrl` に既存のクエリ・フラグメントを含むケース、`endpoint` のフラグメントは明示的に未対応とする。endpoint内の既存クエリ文字列には追加できる。
- リクエスト本文がある場合は既定で `application/json; charset=utf-8` を設定。APIによって異なる場合は `contentType` を指定する。
- `ResponseText` の文字コード解釈はサーバー応答に依存する。JSONの文字列化・解析、認証が必要なプロキシ、システムプロキシの自動検出、TLS証明書の個別設定は対象外。
- `SendApiRequest` は同期実行。応答待ち中は呼び出し側の処理が止まる。タイムアウトは `SetTimeouts` の値で調整する。

**動作確認状況**：実際のWindows/Excel VBAやAPIサーバーでの動作試験は行っていない。GET/POST/PUT/DELETE、プロキシあり/なし、空クエリ、日本語、HTTPエラー、タイムアウトを接続先環境で確認する必要がある。

## 更新履歴

- 2026-11-05：設計メモを、baseUrlとendpointを分離した実コード・呼び出し例に更新。
- 2026-11-05：GET・POSTのエラー判定、認証情報、JSON本文、プロキシ切り替えの例と注意点を追加。
