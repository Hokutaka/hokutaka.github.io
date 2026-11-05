---
title: "VBAからREST APIを呼び出す共通関数"
description: "baseUrlとendpointを分離し、HTTPメソッド・プロキシ・クエリパラメータを切り替えるVBA実装。"
order: 7
category: "プログラミング / VBA"
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

Windows版VBAを想定し、\`WinHttp.WinHttpRequest.5.1\`、\`ADODB.Stream\`、\`Scripting.Dictionary\` を遅延バインディングで利用する。標準モジュールへ貼り付ける想定で、参照設定の追加は不要。

## 実装コード

\`\`\`vb
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

Public Sub ExampleGet()
    Dim params As Object
    Dim response As ApiResponse

    Set params = CreateObject("Scripting.Dictionary")
    params.Add "keyword", "日本語"
    params.Add "page", "1"

    response = SendApiRequest( _
        method:="GET", _
        baseUrl:="https://api.example.com/v1", _
        endpoint:="/items", _
        queryParams:=params _
    )

    Debug.Print response.StatusCode
    Debug.Print response.Body
    If Len(response.ErrorMessage) > 0 Then Debug.Print response.ErrorMessage
End Sub

Public Sub ExamplePostWithProxy()
    Dim response As ApiResponse

    response = SendApiRequest( _
        method:="POST", _
        baseUrl:="https://api.example.com/v1/", _
        endpoint:="items", _
        requestBody:="{""name"":""テスト""}", _
        useProxy:=True, _
        proxyAddress:="proxy.example.com:8080" _
    )

    Debug.Print response.StatusCode, response.Succeeded
    Debug.Print response.Body, response.ErrorMessage
End Sub
\`\`\`

## 呼び出し方

\`ExampleGet\` は次のURLを組み立てる。

\`\`\`text
https://api.example.com/v1/items?keyword=%E6%97%A5%E6%9C%AC%E8%AA%9E&page=1
\`\`\`

クエリパラメータが不要なら \`queryParams\` を省略して呼ぶ。

\`\`\`vb
Dim response As ApiResponse
response = SendApiRequest("DELETE", "https://api.example.com/v1", "/items/123")

response = SendApiRequest( _
    method:="PUT", _
    baseUrl:="https://api.example.com/v1", _
    endpoint:="/items/123", _
    requestBody:="{""name"":""更新後""}" _
)
\`\`\`

\`ExamplePostWithProxy\` は指定したプロキシを経由する。\`useProxy:=False\`（省略時も同じ）ならプロキシを使わず直接接続する。実際のプロキシアドレスは環境に合わせて変更すること。

## 実装の注意

- \`Succeeded\` はHTTPステータス200～299で判定する。HTTP 4xx/5xxは通信成功でも \`Succeeded=False\` とし、\`StatusCode\` と \`Body\` に内容を残す。接続例外時には \`ErrorMessage\` を設定する。
- \`Authorization\` は必要な場合にだけ呼び出し側から渡す。アクセストークンをGitHubにコミットしない。
- \`queryParams\` には \`Scripting.Dictionary\` を渡す想定。同一キーの複数指定や配列値は未対応。
- \`baseUrl\` に既存のクエリ・フラグメントを含むケース、\`endpoint\` のフラグメントは明示的に未対応とする。endpoint内の既存クエリ文字列には追加できる。
- リクエスト本文がある場合は既定で \`application/json; charset=utf-8\` を設定。APIによって異なる場合は \`contentType\` を指定する。
- \`ResponseText\` の文字コード解釈はサーバー応答に依存する。JSONの文字列化・解析、認証が必要なプロキシ、システムプロキシの自動検出、TLS証明書の個別設定は対象外。
- \`SendApiRequest\` は同期実行。応答待ち中は呼び出し側の処理が止まる。タイムアウトは \`SetTimeouts\` の値で調整する。

**動作確認状況**：実際のWindows/Excel VBAやAPIサーバーでの動作試験は行っていない。GET/POST/PUT/DELETE、プロキシあり/なし、空クエリ、日本語、HTTPエラー、タイムアウトを接続先環境で確認する必要がある。

## 更新履歴

- 2026-11-05：設計メモを、baseUrlとendpointを分離した実コード・呼び出し例に更新。
